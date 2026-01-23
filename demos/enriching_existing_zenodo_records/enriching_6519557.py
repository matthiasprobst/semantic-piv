import h5rdmtoolbox as h5tbx
import ssnolib
from h5rdmtoolbox import ld
from h5rdmtoolbox.repository.zenodo import ZenodoRecord
from ontolutils.namespacelib import M4I
from rdflib.namespace import SKOS

ld.BINARY_AS_STRING = True


def main():
    zen = ZenodoRecord(rec_id=6519557)
    GET_METADATA = False
    DOWNLOAD_FIRST_NC_FILE = False

    if GET_METADATA:
        with open("record_metadata", "w") as f:
            for k, v in zen.get_metadata().items():
                f.write(f"{k}: {v}\n")
        with open("record.ttl", "w") as f:
            f.write(zen.as_dcat_dataset().serialize("ttl"))
    if DOWNLOAD_FIRST_NC_FILE:
        for filename, file in zen.files.items():
            file.download(".")
            break  # download only the first file
    # open the nc file:
    nc_filename = "3f80bcb90933658afc743addfb03413e/theta_rad_all_omega_1p0_q_1p8_run_25_1on12.nc"

    file_uri = "https://doi.org/10.5281/zenodo.6519557#"

    from ontolutils.utils.qudt_units import qudt_lookup

    def _get_qudt_unit(value, _):
        return qudt_lookup.get(value, None)

    def _make_standard_name(value, ctx):
        _unit = ctx.get("units", None)
        if _unit is not None:
            units = _get_qudt_unit(_unit, None)
            if units is not None:
                return ssnolib.StandardName(standard_name=value,
                                            unit=units)  # units should be canonical, so this is not yet totally correct
        return None

    rdf_mappings = {
        "units": {
            "predicate": M4I.hasUnit,
            "object": _get_qudt_unit
        },
        "long_name": {
            "predicate": SKOS.altLabel
        },
        "standard_name": {
            "predicate": ssnolib.SSNO,
            "object": _make_standard_name
        }
    }

    # rdf_mappings allow adding rdf properties to the file during serialization without modifying the file itself
    with open("enriched_file_metadata.ttl", "w") as f:
        f.write(
            h5tbx.serialize(
                nc_filename,
                "ttl",
                file_uri=file_uri,
                rdf_mappings=rdf_mappings
            )
        )


if __name__ == "__main__":
    main()
