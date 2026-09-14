"use strict";
// Child process for local learner code. This VM is NOT a security sandbox.
const fs = require("node:fs");
const vm = require("node:vm");
const util = require("node:util");
const { performance } = require("node:perf_hooks");
const MAX_OUTPUT = 12000;
const MAX_RESULT = 512 * 1024;
const filename = "你的代码.js";

function details(error) {
  const stack = String(error.stack || "");
  const found = stack.match(/你的代码\.js:(\d+)/);
  const hints = {
    SyntaxError: "检查括号、引号、花括号和英文标点；函数应定义为 function solve(...)。",
    ReferenceError: "检查变量拼写；先用 let / const 声明，再使用。这里是 Node.js 环境，没有浏览器 document 或 window。",
    TypeError: "检查参数类型和方法名称；数组、字符串、对象支持的方法不同。",
    RangeError: "检查递归终止条件或数组长度是否合理。",
    OutputLimitExceeded: "减少 console.log()，检查无限循环，并只返回题目要求的数据。"
  };
  const name = error.name || "Error";
  return {type: name, message: String(error.message || error).slice(0, 2000),
    line: found ? Number(found[1]) : null,
    hint: hints[name] || "从报错行检查输入值与执行顺序，用 return 返回结果。",
    traceback: stack.slice(0, 4000)};
}

function limitedError(message) {
  const error = new Error(message);
  error.name = "OutputLimitExceeded";
  return error;
}

function normalize(value, state = {count: 0}, depth = 0) {
  if (++state.count > 25000 || depth > 80) throw limitedError("返回值太大或嵌套太深。");
  if (value === undefined || value === null) return null;
  if (typeof value === "string") {
    if (value.length > 100000) throw limitedError("返回的字符串太长。");
    return value;
  }
  if (typeof value === "boolean") return value;
  if (typeof value === "number") {
    if (!Number.isFinite(value)) throw new TypeError("返回值不能包含 NaN 或 Infinity。");
    return value;
  }
  if (Array.isArray(value)) return Array.from(value, item => normalize(item, state, depth + 1));
  if (typeof value === "object" && Object.prototype.toString.call(value) === "[object Object]") {
    return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, normalize(item, state, depth + 1)]));
  }
  throw new TypeError("请返回数字、字符串、布尔值、数组或普通对象；Set/Map 需要先转换。");
}

function equal(actual, expected) {
  if (typeof actual === "number" && typeof expected === "number") {
    if (Number.isInteger(actual) && Number.isInteger(expected)) return actual === expected;
    return Math.abs(actual - expected) <= Math.max(1e-8, 1e-6 * Math.max(Math.abs(actual), Math.abs(expected)));
  }
  if (Array.isArray(actual) && Array.isArray(expected)) {
    return actual.length === expected.length && actual.every((item, index) => equal(item, expected[index]));
  }
  if (actual !== null && expected !== null && typeof actual === "object" && typeof expected === "object") {
    const keys = Object.keys(actual);
    return keys.length === Object.keys(expected).length && keys.every(key => Object.hasOwn(expected, key) && equal(actual[key], expected[key]));
  }
  return actual === expected;
}

async function evaluate(payload) {
  const start = performance.now();
  const result = {status: "accepted", passed: 0, total: payload.cases.length, cases: [], error: null, duration_ms: 0, mode: payload.mode || "run"};
  let script;
  try {
    script = new vm.Script(payload.code + "\n;typeof solve === 'function' ? solve : null", {filename});
  } catch (error) {
    result.status = "syntax_error";
    result.error = details(error);
    return result;
  }
  for (const test of payload.cases) {
    let output = "";
    const record = {passed: false, args: structuredClone(test.args), expected: test.expected ?? null, actual: null, stdout: ""};
    const timers = new Set();
    const intervals = new Set();
    function print(...values) {
      const text = util.format(...values) + "\n";
      if (output.length + text.length > MAX_OUTPUT) {
        output += text.slice(0, Math.max(0, MAX_OUTPUT - output.length));
        throw limitedError("打印内容超过平台上限。");
      }
      output += text;
    }
    try {
      const context = vm.createContext({
        console: {log: print, info: print, warn: print, error: print, debug: print, table: print},
        require, Buffer, URL, URLSearchParams, TextEncoder, TextDecoder, AbortController, AbortSignal,
        fetch: globalThis.fetch, structuredClone,
        setTimeout: (fn, delay, ...args) => {const timer = setTimeout(fn, delay, ...args); timers.add(timer); return timer;},
        clearTimeout, setInterval: (fn, delay, ...args) => {const timer = setInterval(fn, delay, ...args); intervals.add(timer); return timer;}, clearInterval
      });
      const solve = script.runInContext(context);
      if (typeof solve !== "function") throw new TypeError("找不到 solve 函数，请保留 function solve(...)。");
      const actual = await solve(...structuredClone(test.args));
      record.actual = normalize(actual);
      record.passed = !!test.custom || equal(record.actual, test.expected);
      if (test.custom) {record.custom = true; record.label = "执行成功";}
      if (!record.passed && actual === undefined) record.hint = "函数没有返回值。console.log() 只显示内容，请用 return 返回结果。";
      if (record.passed) result.passed++;
      else if (result.status === "accepted") result.status = "wrong_answer";
    } catch (error) {
      record.error = details(error);
      result.error = record.error;
      result.status = "runtime_error";
    } finally {
      for (const timer of timers) clearTimeout(timer);
      for (const timer of intervals) clearInterval(timer);
    }
    record.stdout = output;
    result.cases.push(record);
    if (record.error) break;
  }
  result.duration_ms = Math.round(performance.now() - start);
  return result;
}

(async () => {
  const payload = JSON.parse(fs.readFileSync(0, "utf8"));
  let result;
  if (Array.isArray(payload.batch)) {
    result = [];
    for (const item of payload.batch) result.push(await evaluate(item));
  } else result = await evaluate(payload);
  let text = JSON.stringify(result);
  if (Buffer.byteLength(text) > MAX_RESULT) text = JSON.stringify({status: "runtime_error", passed: 0, total: payload.cases?.length || 0, cases: [], mode: payload.mode || "run", duration_ms: 0, error: details(limitedError("返回结果或打印内容过大。"))});
  process.stdout.write(text);
})().catch(error => {
  process.stdout.write(JSON.stringify({status: "runtime_error", passed: 0, total: 0, cases: [], mode: "run", duration_ms: 0, error: details(error)}));
});
