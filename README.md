# Qualifying Variant Set Standard (QVSS)

## Standard

The Qualifying Variant Set Standard (QVSS) defines a minimal, interoperable representation of rule-based criteria used to determine whether records of genetic variation qualify under a declared genomic analysis context.

The LaTeX and HTML versions of the standard can be found in the `latex/` and `html/` folders.

## Layout

```text
artefacts/
  README.md
  SHA256SUMS.txt
  schema/
    qvss-1.0.schema.json
  examples/
    builder_examples/
    valid/
    invalid/
  fixtures/
  templates/
  profiles/
  resources/
  tools/
html/
latex/
```

## Artefacts

The `artefacts/` folder contains the implementation artefacts for the Qualifying Variant Set Standard (QVSS) 1.0.  We provide the schema, examples, fixtures, templates, and small profile notes needed by implementers.

QVSS represents qualifying variant criteria. It does not define variant calling, annotation correctness, clinical validity, pathogenicity, reportability, statistical significance, or downstream interpretation.

### Contents

| Path | Purpose |
|---|---|
| `schema/qvss-1.0.schema.json` | JSON Schema for structural validation of QVSS 1.0 files. |
| `examples/valid/` | Valid QVSS examples for common genomics, clinical genetics, GWAS, and WGS QC cases. |
| `examples/invalid/` | Intentionally invalid files for validator and conformance testing. |
| `examples/builder_examples/` | Examples of text-based single line entries used with a QV set builder to convert to YAML. |
| `fixtures/` | Expected outcomes for rule logic, missing values, and example records. |
| `templates/` | Registry and QV application record templates. |
| `profiles/` | Short notes for profile-defined behaviour used in examples. |
| `resources/` | Small placeholder resources used by examples. |
| `tools/` | Minimal validation helper for local checks. |
| `SHA256SUMS.txt` | File-byte checksums for this publication package. |

### Valid examples

| File | Shows |
|---|---|
| `example_minimal_qv_set.yaml` | Minimal atomic numeric rule. |
| `example_gwas_common_qc.yaml` | Common GWAS QC thresholds. |
| `example_panel_overlap.yaml` | BED-style panel overlap with resource metadata. |
| `example_variant_flag_exclusion.yaml` | `not` around `contains`, used for exclusion flags. |
| `example_commercial_wgs_variant_qc.yaml` | Variant-level commercial WGS QC using `QUAL`, `DP`, `GQ`, and `FILTER`. |
| `example_clinical_rare_variant.yaml` | Rare variant qualification using frequency, consequence, and exclusion flags. |
| `example_secondary_findings_panel.yaml` | Gene-list based secondary findings style qualification. |
| `example_wgs_sample_qc.yaml` | Sample-level WGS QC before variant interpretation. |
| `example_compound_het_profile.yaml` | Profile-defined aggregation for compound heterozygosity. |
| `example_cnv_sv_qc.yaml` | CNV/SV style qualification using size, quality, and blacklist flags. |

### Invalid examples

| File | Expected problem |
|---|---|
| `invalid_missing_operator.yaml` | A field-resolving rule has no operator. |
| `invalid_unsupported_operator_not_contains.yaml` | `not_contains` is not a core operator. Use `not` around `contains`. |
| `invalid_incompatible_datatype.yaml` | Numeric comparison is declared but the value is a string. This is a semantic conformance failure. |

### Builder examples

The builder syntax is an authoring convenience for people who do not want to write YAML or JSON directly. 
A public QV set builder is available from [Switzerland Omics](https://switzerlandomics.ch/pages/qv_builder/).

It uses simple statement types:

- `meta` for QV set metadata
- `filter` for simple atomic rules
- `criteria` for criteria, compound logic, references, or profile-defined statements
- `note` for non-normative notes

These examples are intended to generate readable draft YAML. Before registry publication, convert or normalise the generated YAML to the normative QVSS 1.0 layout with `qvss_version`, declared inputs, resources, profiles, and `qualification` where required.

Some examples of logic building exist. For instance, there is no `not_contains` operator. Use `logic=not` around `operator=contains`:

```text
criteria no_low_confidence_flag logic=not desc="Variant must not contain a low confidence flag"
criteria no_low_confidence_flag field=FILTER operator="contains" value=low_confidence missing=fail
```

With `missing=fail` on the inner `contains` condition, a missing field fails the inner test and therefore passes the outer `not` rule.


| File | Shows |
| --- | --- |
| `00_minimal_qv_set.txt` | minimal quality threshold |
| `01_gwas_common_qc.txt` | common GWAS QC thresholds |
| `02_panel_overlap.txt` | disease panel or BED overlap |
| `03_variant_flag_exclusion.txt` | must-not-contain using `logic=not` around `operator=contains` |
| `04_commercial_wgs_variant_qc.txt` | commercial WGS variant-level QC |
| `05_clinical_rare_variant.txt` | rare clinical genetics variant qualification |
| `06_secondary_findings_panel.txt` | secondary findings panel example |
| `07_wgs_sample_qc.txt` | sample-level WGS QC |
| `08_compound_het_profile.txt` | profile-defined compound heterozygosity example |
| `09_cnv_sv_qc.txt` | CNV and structural variant QC example |

### Check locally

Install Python dependencies if needed:

```bash
pip install jsonschema pyyaml
```

Validate the examples:

```bash
python tools/validate_qvss_examples.py
```

The helper checks JSON Schema validity and a small set of semantic rules used by the examples. It is not a clinical or biological validator.

## Checksum policy

QVSS 1.0 registries should state whether a checksum applies to exact released file bytes or to a canonical representation. This package uses `file-bytes` checksums.
