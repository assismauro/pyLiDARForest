rem python validateLAS.py -c 11 -v 0 -m 4 -z 20 -x 20.0 -l 1.2 h:\transects\NP_T-????.las -vfp VALIDATE_FILES -csv h:\transects\result1000.csv -sv 1,2,3,4,5,6,7
python validateLAS.py -c 13 -v 0 -m 4 -z 20 -x 20.0 -l 1.3 G:\TRANSECTS\VALIDATING\*.LAZ -vfp VALIDATE_FILES -csv h:\transects\result1000_fwf.csv -sv 1,2,3,4,5,6,7,8


python validateLAS.py -c 13 -v 0 -m 4 -z 20 -x 20.0 -l 1.3 G:\TRANSECTS\T-1016\NP_T-1016_FWF_LAS\np_t-1016.las -vfp VALIDATE_FILES -csv 1016.csv -sv 1,2,3,4,5,6,7,8 -v 1
python validateLAS.py  G:\TRANSECTS\T-1021\NP_T-1021_FWF_LAS\np_t-1021.las -c 13 -v 0 -m 4 -z 20 -x 20.0 -l 1.3 -vfp VALIDATE_FILES -csv 1021.csv -sv 1,2,3,4,5,6,7,8 -v 1

python importcsv2postgres.py E:\mauro.assis\pyLiDARForest\validate_fwf.csv -s localhost -u postgres -p ebaeba18 -c -t _validate -d eba -sf 3 -cn -nv -


python importcsv2postgres.py E:\mauro.assis\pyLiDARForest\validate\validate_fwf.csv -s localhost -u postgres -p ebaeba18 -c -t _validate -d eba -sf 3 -cn -nv -


python validateLAS.py H:\TRANSECTS_SEGUNDA_CAMPANHA\*.LAS -c 2 -v 0 -m 4 -z 20 -x 20.0 -l 1.3 -vfp VALIDATE_FILES -csv h:\transects\VALIDATE.csv -sv 1,2,3,4,5,6,7,8


s = '{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13},{14},{15},{16},{17},{18},{19},{20},'.format(
    '' if fname.upper().endswith('LAZ') else header.guid,
    header.file_source_id,
    header.global_encoding,
    '' if fname.upper().endswith('LAZ') else header.project_id,
    header.version,
    header.date,
    header.system_id.strip('\x00'),
    header.software_id.strip('\x00'),
    header.point_records_count,
    header.scale[0], header.scale[1], header.scale[2],
    header.offset[0], header.offset[1], header.offset[2],
    header.min[0], header.min[1], header.min[2],
    header.max[0], header.max[1], header.max[2])
