// Example view data (JavaScript)
// https://standardschema.dev/
const resource = {
  name: "World",
  repo: "World",
  owner: "World",
  greet: function (text) {
    return "Hello, " + text + "!";
  },
};
const Mustache = require("mustache");

const context = {
  provider: {
    name: "addy mail",
    resources: ["domain", "mail_alias", "InboundRoute", "outbound-route"],
  },
  owner: "AcmeCorp",

  capitalize: function (text, render) {
    const rendered = render(text);
    return rendered.replace(/\b(\w)/g, (c) => c.toUpperCase());
  },

  camel: function (text, render) {
    const s = render(text).trim();
    // Normalize separators to single spaces first
    return s
      .replace(/[_\-]+/g, " ")
      .split(/\s+/)
      .map((part, i) =>
        i === 0
          ? part.toLowerCase()
          : part.charAt(0).toUpperCase() + part.slice(1).toLowerCase(),
      )
      .join("");
  },

  snake: function (text, render) {
    let s = render(text).trim();
    // Break camelCase / PascalCase boundaries
    s = s.replace(/([a-z0-9])([A-Z])/g, "$1_$2");
    // Normalize separators to underscore
    s = s.replace(/[\s\-]+/g, "_");
    return s.toLowerCase();
  },
};

const output = Mustache.render(
  require("fs").readFileSync("template.mustache", "utf8"),
  context,
);

console.log(output);
