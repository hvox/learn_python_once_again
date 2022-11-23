#include <Python.h>
#define MODULO(x, y) ((x) % (y) + (y)) % (y)

static PyObject *pow_mod(PyObject *self, PyObject *args) {
	int64_t x, y, mod;
	if (!PyArg_ParseTuple(args, "lll", &x, &y, &mod))
		return NULL;
	if (mod < 0)
		mod = -mod;
	if (mod <= 1 && mod >= -1)
		return PyLong_FromLong(0);
	int64_t result = 1;
	if (y < 0)
		y = MODULO(y, mod - 1);
	for (; y > 0; y /= 2) {
		if (y % 2)
			result = result * x % mod;
		x = x * x % mod;
	}
	return PyLong_FromLong(result);
}

PyMethodDef method_table[] = {
    {"pow", (PyCFunction)pow_mod, METH_VARARGS, "Find x**y % mod"},
    {NULL, NULL, 0, NULL} // End marker of method table
};

PyModuleDef aboba_module = {
    PyModuleDef_HEAD_INIT,
    "aboba",      // Name
    "Aboba",      // Docstring
    -1,           // Size of the module state memory
    method_table, // Table of methods
    NULL,         // Slot definitions
    NULL,         // Traversal function
    NULL,         // Clear function
    NULL          // Module deallocation function
};

PyMODINIT_FUNC PyInit_aboba(void) { return PyModule_Create(&aboba_module); }
