#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>

#include "py/bc.h"
#include "py/compile.h"
#include "py/persistentcode.h"
#include "py/runtime.h"
#include "py/gc.h"
#include "py/stackctrl.h"
#ifdef _WIN32
#include "ports/windows/fmode.h"
#endif

// Heap size of GC heap (if enabled)
// Make it larger on a 64 bit machine, because pointers are larger.
long heap_size = 1024*1024 * (sizeof(mp_uint_t) / 4);

STATIC void stderr_print_strn(void *env, const char *str, mp_uint_t len) {
    (void)env;
    ssize_t dummy = write(STDERR_FILENO, str, len);
    (void)dummy;
}

STATIC const mp_print_t mp_stderr_print = {NULL, stderr_print_strn};

STATIC void recursive_disassemble(const mp_raw_code_t *rc) {
    if (rc->kind != MP_CODE_BYTECODE) {
        return;
    }

    mp_bytecode_print(rc, rc->data.u_byte.bytecode, rc->data.u_byte.bc_len, rc->data.u_byte.const_table);

    // Constant table: positional + keyword-only argument names, then objects, then nested raw-code pointers.
    // We have to skip more than just objects, so we don't interpret a function containing a lambda or nested function as a pointer
    const byte *prelude = rc->data.u_byte.bytecode;
    mp_decode_uint(&prelude); // n_state
    mp_decode_uint(&prelude); // n_exc_stack
    prelude++; // scope_flags
    const size_t n_pos_args = *prelude++;
    const size_t n_kwonly_args = *prelude++;
    const size_t raw_code_offset = n_pos_args + n_kwonly_args + rc->data.u_byte.n_obj;

    for(size_t i = 0; i < rc->data.u_byte.n_raw_code; i++) {
        const mp_raw_code_t *nrc = (const mp_raw_code_t*)rc->data.u_byte.const_table[raw_code_offset + i];
        recursive_disassemble(nrc);
    }
}

STATIC void disassemble(const char *file) {
	const mp_raw_code_t *rc = mp_raw_code_load_file(file);
	recursive_disassemble(rc);
}

MP_NOINLINE int main_(int argc, char **argv) {
    mp_stack_set_limit(40000 * (BYTES_PER_WORD / 4));

    char *heap = malloc(heap_size);
    gc_init(heap, heap + heap_size);

    mp_init();
#ifdef _WIN32
    set_fmode_binary();
#endif
    mp_obj_list_init(mp_sys_path, 0);
    mp_obj_list_init(mp_sys_argv, 0);

    // set default compiler configuration
    mp_dynamic_compiler.small_int_bits = 31;
    mp_dynamic_compiler.opt_cache_map_lookup_in_bytecode = 0;
    mp_dynamic_compiler.py_builtins_str_unicode = 1;

    if (argc <= 1) {
        mp_printf(&mp_stderr_print, "no input file\n");
        exit(1);
    }

    const char *input_file = argv[1];

    disassemble(input_file);

    mp_deinit();

    return 0;
}

int main(int argc, char **argv) {
    mp_stack_ctrl_init();
    return main_(argc, argv);
}

uint mp_import_stat(const char *path) {
    (void)path;
    return MP_IMPORT_STAT_NO_EXIST;
}

void nlr_jump_fail(void *val) {
    printf("FATAL: uncaught NLR %p\n", val);
    exit(1);
}
