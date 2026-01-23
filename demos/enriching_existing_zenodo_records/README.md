# README

This demo downloads one nc file from the zenodo record
and enriches it with some metadata by applying an RDF mapping.


Example below shows that the `time` dataset from the nc file gets the predicate skos:altLabel, because
the the dataset has the attribute `long_name`, which is interpreted as a label.

    <https://doi.org/10.5281/zenodo.6519557#theta_rad_all_omega_1p0_q_1p8_run_25_1on12.nc/time> a hdf:Dataset ;
    hdf:attribute <https://doi.org/10.5281/zenodo.6519557#theta_rad_all_omega_1p0_q_1p8_run_25_1on12.nc/time@_Netcdf4Dimid>,
        <https://doi.org/10.5281/zenodo.6519557#theta_rad_all_omega_1p0_q_1p8_run_25_1on12.nc/time@bounds>,
        <https://doi.org/10.5281/zenodo.6519557#theta_rad_all_omega_1p0_q_1p8_run_25_1on12.nc/time@calendar>,
        <https://doi.org/10.5281/zenodo.6519557#theta_rad_all_omega_1p0_q_1p8_run_25_1on12.nc/time@calendar_type>,
        <https://doi.org/10.5281/zenodo.6519557#theta_rad_all_omega_1p0_q_1p8_run_25_1on12.nc/time@cartesian_axis>,
        <https://doi.org/10.5281/zenodo.6519557#theta_rad_all_omega_1p0_q_1p8_run_25_1on12.nc/time@long_name>,
        <https://doi.org/10.5281/zenodo.6519557#theta_rad_all_omega_1p0_q_1p8_run_25_1on12.nc/time@units> ;
    hdf:chunk <https://doi.org/10.5281/zenodo.6519557#theta_rad_all_omega_1p0_q_1p8_run_25_1on12.nc/time__chunk_dimensions> ;
    hdf:dataspace <https://doi.org/10.5281/zenodo.6519557#theta_rad_all_omega_1p0_q_1p8_run_25_1on12.nc/time__dataspace> ;
    hdf:datatype hdf:H5T_FLOAT,
        hdf:H5T_IEEE_F64LE ;
    hdf:layout hdf:H5D_CHUNKED ;
    hdf:maximumSize -1 ;
    hdf:name "/time" ;
    hdf:rank 1 ;
    hdf:size 0 ;
    m4i:hasUnit <None> ;
    skos:altLabel "time" .