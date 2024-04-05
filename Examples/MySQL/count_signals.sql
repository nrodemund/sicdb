/*

An example of a query that counts the amount of signals contained in the data_float_h table, including the reference name. This is a long running query, as it processes a large amount of rows.

*/



SELECT 
  d_references.ReferenceValue as data_name, 
  Sum(cnt) as data_count 
FROM 
  `data_float_h` 
  LEFT JOIN d_references ON d_references.ReferenceGlobalID = data_float_h.DataID 
GROUP BY 
  DataID 
ORDER by 
  data_count DESC