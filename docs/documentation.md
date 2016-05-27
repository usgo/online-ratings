# Getting Started

1. Ensure `mkdocs` is installed.
2. Run `mkdocs serve` from within the root of `online-ratings`.
3. Load it in a browser and profit!

# Making non-API Pages

Create or edit the `.md` files within `docs/`.

Refer to [mkdocs][0] for more details.

# Generating API Documentation

Source files to be edited can be found in `docs/schemata`.  The files are in [YAML][1] for improved
readability.

1. Install [prmd][2] per their instructions.
2. From root of `online-ratings`, run
   `prmd combine --meta docs/meta.yml --output docs/schema.json docs/schemata`
3. From root of `online-ratings`, run `prmd doc --output docs/api.md docs/schema.json`

[JSON Schema][3] is the general format used for types and [JSON Hyper-Schema][4] is used for
endpoint definitions.

# Deploying

1. Run `mkdocs gh-deploy --clean`.
2. That's it!

[0]: http://www.mkdocs.org/
[1]: https://en.wikipedia.org/wiki/YAML
[2]: https://github.com/interagent/prmd
[3]: http://json-schema.org/documentation.html
[4]: http://json-schema.org/latest/json-schema-hypermedia.html
