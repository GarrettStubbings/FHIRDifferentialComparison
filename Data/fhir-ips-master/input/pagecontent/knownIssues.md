### Known Issues
1. Lack in representation of the summarization activities, including who did it, what was done (medication reconciliation, allergy reconciliation, medication allergy reconciliation, immunization/vaccination reconciliation, problem list/diagnosis reconciliation), what was the result, when and where was it done. This covers also the "Nature of the IPS" element included in EN 17269 and ISO/DIS 27269.
1. Profile specificity to be improved. Not all the expected rules can be automatically validated, due to a lack of representation in the specified profiles.
1. All of the slicing rules defined for the section entries have been specified in this version as open. This choice has been made to give more flexibility to the IPS, at the expense of the capability of fully and automatically validating the instances. In this sense the profile may technically allow the inclusion of inappropriate resources. Specifiers are encouraged to add further constraints or additional slices to mitigate this risk. Future versions may reconsider the current choice.
1. More constrained vocabularies. The choices made in this version reflect the need of balancing the expectations of reducing optionality, to improve interoperability; and of avoiding over-constraints, to facilitate the local adoption. Moreover, it has been recognized the current lack, in some cases, of globally recognized and freely usable vocabularies (e.g. for the identification of medications); and the need, for specific concept domains, to extend the value sets based on the SNOMED Int. Global Patient Set. For these reasons, the binding is required only in a few cases; preferred or extensible bindings have been used instead.
1. MedicationStatement-uv-ips profile, the binding for element category reads erroneously "Medication Status Codes (preferred)", it should read "Medication statement categories" instead. This comes from a typo in the value set title in the current published FHIR R4 specification (see FHIR issue tracker [FHIR-23979](https://jira.hl7.org/browse/FHIR-23979)).

### Future Development
1. Investigate the relationships and the possible synergies with the proposed [International Patient Access Implementation Guide](https://build.fhir.org/ig/grahamegrieve/ipa-candidate/); exploring and better clarifying the role of the IPS document and of its reusable components (IPS profiles library).
1. Specify how to send or get IPS documents or IPS resources by using FHIR APIs.
1. Explore the adoption of the Provenance resource with the IPS (bundle level, composition level or entry level) to document the IPS curation (see Known Issue ###1 above) (see also the ["International Patient Summary: Use Cases"](https://confluence.hl7.org/pages/viewpage.action?pageId=48237134###InternationalPatientSummary:UseCases-Examples) confluence page)