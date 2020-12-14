var SiteJS = typeof SiteJS === "object" ? SiteJS : {}; SiteJS["pegasus"] =
/******/ (function(modules) { // webpackBootstrap
/******/ 	// The module cache
/******/ 	var installedModules = {};
/******/
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/
/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId]) {
/******/ 			return installedModules[moduleId].exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			i: moduleId,
/******/ 			l: false,
/******/ 			exports: {}
/******/ 		};
/******/
/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/
/******/ 		// Flag the module as loaded
/******/ 		module.l = true;
/******/
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/
/******/
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;
/******/
/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;
/******/
/******/ 	// define getter function for harmony exports
/******/ 	__webpack_require__.d = function(exports, name, getter) {
/******/ 		if(!__webpack_require__.o(exports, name)) {
/******/ 			Object.defineProperty(exports, name, { enumerable: true, get: getter });
/******/ 		}
/******/ 	};
/******/
/******/ 	// define __esModule on exports
/******/ 	__webpack_require__.r = function(exports) {
/******/ 		if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 			Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 		}
/******/ 		Object.defineProperty(exports, '__esModule', { value: true });
/******/ 	};
/******/
/******/ 	// create a fake namespace object
/******/ 	// mode & 1: value is a module id, require it
/******/ 	// mode & 2: merge all properties of value into the ns
/******/ 	// mode & 4: return value when already ns object
/******/ 	// mode & 8|1: behave like require
/******/ 	__webpack_require__.t = function(value, mode) {
/******/ 		if(mode & 1) value = __webpack_require__(value);
/******/ 		if(mode & 8) return value;
/******/ 		if((mode & 4) && typeof value === 'object' && value && value.__esModule) return value;
/******/ 		var ns = Object.create(null);
/******/ 		__webpack_require__.r(ns);
/******/ 		Object.defineProperty(ns, 'default', { enumerable: true, value: value });
/******/ 		if(mode & 2 && typeof value != 'string') for(var key in value) __webpack_require__.d(ns, key, function(key) { return value[key]; }.bind(null, key));
/******/ 		return ns;
/******/ 	};
/******/
/******/ 	// getDefaultExport function for compatibility with non-harmony modules
/******/ 	__webpack_require__.n = function(module) {
/******/ 		var getter = module && module.__esModule ?
/******/ 			function getDefault() { return module['default']; } :
/******/ 			function getModuleExports() { return module; };
/******/ 		__webpack_require__.d(getter, 'a', getter);
/******/ 		return getter;
/******/ 	};
/******/
/******/ 	// Object.prototype.hasOwnProperty.call
/******/ 	__webpack_require__.o = function(object, property) { return Object.prototype.hasOwnProperty.call(object, property); };
/******/
/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "";
/******/
/******/
/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(__webpack_require__.s = "./assets/javascript/pegasus/pegasus.js");
/******/ })
/************************************************************************/
/******/ ({

/***/ "./assets/javascript/api.js":
/*!**********************************!*\
  !*** ./assets/javascript/api.js ***!
  \**********************************/
/*! exports provided: getAction, Api */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, \"getAction\", function() { return getAction; });\n/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, \"Api\", function() { return Api; });\nfunction _createForOfIteratorHelper(o, allowArrayLike) { var it; if (typeof Symbol === \"undefined\" || o[Symbol.iterator] == null) { if (Array.isArray(o) || (it = _unsupportedIterableToArray(o)) || allowArrayLike && o && typeof o.length === \"number\") { if (it) o = it; var i = 0; var F = function F() {}; return { s: F, n: function n() { if (i >= o.length) return { done: true }; return { done: false, value: o[i++] }; }, e: function e(_e) { throw _e; }, f: F }; } throw new TypeError(\"Invalid attempt to iterate non-iterable instance.\\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.\"); } var normalCompletion = true, didErr = false, err; return { s: function s() { it = o[Symbol.iterator](); }, n: function n() { var step = it.next(); normalCompletion = step.done; return step; }, e: function e(_e2) { didErr = true; err = _e2; }, f: function f() { try { if (!normalCompletion && it[\"return\"] != null) it[\"return\"](); } finally { if (didErr) throw err; } } }; }\n\nfunction _unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === \"string\") return _arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === \"Object\" && o.constructor) n = o.constructor.name; if (n === \"Map\" || n === \"Set\") return Array.from(o); if (n === \"Arguments\" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return _arrayLikeToArray(o, minLen); }\n\nfunction _arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }\n\nfunction getAction(apiRoot, action) {\n  // DRF dynamically sets the apiRoot based on the common shared prefix, so we attempt\n  // to inspect window.schema for the action - first searching for the namespaced version,\n  // then trying the action directly\n  var namespacedAction = apiRoot.concat(action);\n\n  if (!window.schema) {\n    console.error(\"window.schema not found. Did you forget to load your schemajs?\");\n  } else if (pathExistsInObject(action, window.schema.content)) {\n    return action;\n  } else if (pathExistsInObject(namespacedAction, window.schema.content)) {\n    return namespacedAction;\n  } else {\n    // fall back to default, even though it may not be valid\n    console.error('action ' + namespacedAction + 'not found in API schema. Some functionality may not work.');\n  }\n\n  return apiRoot.concat(action);\n}\n\nfunction pathExistsInObject(path, schema) {\n  var currentSchema = schema;\n\n  var _iterator = _createForOfIteratorHelper(path),\n      _step;\n\n  try {\n    for (_iterator.s(); !(_step = _iterator.n()).done;) {\n      var pathPart = _step.value;\n\n      if (currentSchema) {\n        currentSchema = currentSchema[pathPart];\n      } else {\n        return false;\n      }\n    }\n  } catch (err) {\n    _iterator.e(err);\n  } finally {\n    _iterator.f();\n  }\n\n  return Boolean(currentSchema);\n}\n\nvar Api = {\n  getAction: getAction\n};\n\n//# sourceURL=webpack://SiteJS.%5Bname%5D/./assets/javascript/api.js?");

/***/ }),

/***/ "./assets/javascript/pegasus/examples/charts.js":
/*!******************************************************!*\
  !*** ./assets/javascript/pegasus/examples/charts.js ***!
  \******************************************************/
/*! exports provided: Charts */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, \"Charts\", function() { return Charts; });\n/* harmony import */ var _const__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./const */ \"./assets/javascript/pegasus/examples/const.js\");\n/* harmony import */ var _api__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../../api */ \"./assets/javascript/api.js\");\n\n\n\n\n\nfunction renderChart(chartType, bindTo, data) {\n  c3.generate({\n    bindto: bindTo,\n    data: {\n      columns: data,\n      type: chartType\n    }\n  });\n}\n\nfunction getListEmployeesAction() {\n  return Object(_api__WEBPACK_IMPORTED_MODULE_1__[\"getAction\"])(_const__WEBPACK_IMPORTED_MODULE_0__[\"API_ROOT\"], [\"employee-data\", \"list\"]);\n}\n\nvar Charts = {\n  renderChart: renderChart,\n  getListEmployeesAction: getListEmployeesAction\n};\n\n//# sourceURL=webpack://SiteJS.%5Bname%5D/./assets/javascript/pegasus/examples/charts.js?");

/***/ }),

/***/ "./assets/javascript/pegasus/examples/const.js":
/*!*****************************************************!*\
  !*** ./assets/javascript/pegasus/examples/const.js ***!
  \*****************************************************/
/*! exports provided: API_ROOT */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, \"API_ROOT\", function() { return API_ROOT; });\n// if your API lives at a different namespace you can add it here\n// e.g. API_ROOT = [\"myapp\", \"api\"];\nvar API_ROOT = [\"pegasus\", \"api\"];\n\n//# sourceURL=webpack://SiteJS.%5Bname%5D/./assets/javascript/pegasus/examples/const.js?");

/***/ }),

/***/ "./assets/javascript/pegasus/pegasus.js":
/*!**********************************************!*\
  !*** ./assets/javascript/pegasus/pegasus.js ***!
  \**********************************************/
/*! exports provided: Charts */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _examples_charts__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./examples/charts */ \"./assets/javascript/pegasus/examples/charts.js\");\n/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, \"Charts\", function() { return _examples_charts__WEBPACK_IMPORTED_MODULE_0__[\"Charts\"]; });\n\n\n\n//# sourceURL=webpack://SiteJS.%5Bname%5D/./assets/javascript/pegasus/pegasus.js?");

/***/ })

/******/ });