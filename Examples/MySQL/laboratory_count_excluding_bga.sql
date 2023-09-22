/*

Retrieves a comprehensive list of laboratory values excluding blood gas analysis, including their names and corresponding units of measurement, and present the results in descending order based on their frequency count.

*/


SELECT 
  COUNT(id) as laboratory_count, 
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
