const { defineConfig } = require("@playwright/test");

module.exports = defineConfig({
  testDir: "./tests",
  timeout: 30_000,
  expect: {
    timeout: 5_000
  },
  use: {
    baseURL: "http://127.0.0.1:4174",
    trace: "on-first-retry"
  },
  webServer: {
    command: "PORT=4174 node server.js",
    url: "http://127.0.0.1:4174",
    reuseExistingServer: true,
    timeout: 120_000
  }
});
