/*

Retrieves a comprehensive list of laboratory values excluding blood gas analysis, including count, mean, standard deviation, names and corresponding units of measurement, and present the results in descending order based on their frequency count.

*/


SELECT 
  COUNT(id) as laboratory_count, 
  AVG(LaboratoryValue) as laboratory_value_mean, 
  STDDEV(LaboratoryValue) as laboratory_standard_deviation, 
  r.ReferenceValue as laboratory_name, 
  r.ReferenceUnit as laboratory_unit_of_measurement 
FROM 
  `laboratory` 
  LEFT JOIN d_references as r ON r.ReferenceGlobalID = LaboratoryID 
WHERE 
  r.ReferenceValue NOT LIKE '%(BGA)%' 
GROUP BY 
  LaboratoryID 
ORDER BY 
  laboratory_count DESC;
