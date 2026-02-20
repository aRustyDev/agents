const fs = require('node:fs')
const path = require('node:path')

function pascalCase(str) {
  return str.replace(/(^|[-_])([a-z])/g, (_, _sep, c) => c.toUpperCase())
}

function renderLicense(license) {
  if (typeof license === 'string') return `"${license}"`
  if (license.all_of) return `all_of: [${license.all_of.map((l) => `"${l}"`).join(', ')}]`
  if (license.any_of) return `any_of: [${license.any_of.map((l) => `"${l}"`).join(', ')}]`
  return '"MIT"'
}

function preprocessFormulas(formulas) {
  for (const formula of formulas) {
    formula.class_name = pascalCase(formula.name)
    formula.formula_name = formula.name
    formula.license_rendered = renderLicense(formula.license)

    if (formula.language) {
      formula[`is_${formula.language}`] = true
    }

    if (formula.install) {
      Object.assign(formula, formula.install)
      if (formula.install.build_system) {
        formula[`build_system_is_${formula.install.build_system}`] = true
      }
    }

    if (formula.service) {
      if (Array.isArray(formula.service.run)) {
        formula.service.run_is_array = true
        formula.service.run_rendered = `[${formula.service.run.map((s) => `"${s}"`).join(', ')}]`
      } else {
        formula.service.run_rendered = `"${formula.service.run}"`
      }
      if (typeof formula.service.keep_alive !== 'undefined') {
        formula.service.keep_alive_bool = true
        formula.service.keep_alive_rendered = JSON.stringify(formula.service.keep_alive)
      }
    }
  }
}

function loadPartials(langsDir) {
  const partials = {}
  for (const file of fs.readdirSync(langsDir)) {
    if (file.endsWith('.mustache')) {
      const name = `langs/${path.basename(file, '.mustache')}`
      partials[name] = fs.readFileSync(path.join(langsDir, file), 'utf8')
    }
  }
  return partials
}

function parseInput(input) {
  try {
    if ((input.startsWith('/') || input.startsWith('.')) && fs.existsSync(input)) {
      return fs.readFileSync(input, 'utf8')
    }
  } catch {}
  return input
}

module.exports = {
  pascalCase,
  renderLicense,
  preprocessFormulas,
  loadPartials,
  parseInput,
}
