#define PY_SSIZE_T_CLEAN
#include <Python.h>

typedef struct {
	PyObject_HEAD
} AbobaObject;

static PyTypeObject AbobaType = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_name = "aboba.Aboba",
    .tp_doc = PyDoc_STR("Aboba objects"),
    .tp_basicsize = sizeof(AbobaObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
};

PyMethodDef method_table[] = {
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

PyMODINIT_FUNC PyInit_aboba(void) {
	if (PyType_Ready(&AbobaType) < 0)
		return NULL;
	PyObject *module = PyModule_Create(&aboba_module);
	if (module == NULL)
		return NULL;
	Py_INCREF(&AbobaType);
	if (PyModule_AddObject(module, "Aboba", (PyObject *)&AbobaType) < 0) {
		Py_DECREF(&AbobaType);
		Py_DECREF(module);
		return NULL;
	}
	return module;
}
