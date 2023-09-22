/*

This query fetches the initial creatinine results (identified by laboratory ID 367) for patients in the intensive care unit, excluding prior laboratory values. Although it might seem more logical to start with the laboratory as the base table, this approach significantly increases query time. It's important to note that when using this method, subqueries need to be repeated because MySQL can retrieve only one value from scalar subqueries.


*/



SELECT 
  `cases`.`CaseID` AS CaseID, 
  ICUOffset, 
  (
    SELECT 
      laboratory.LaboratoryValue 
    FROM 
      laboratory 
    WHERE 
      laboratory.CaseID = cases.CaseID 
      AND laboratory.LaboratoryID = 367 
      AND Offset >= ICUOffset 
    ORDER BY 
      laboratory.Offset ASC 
    LIMIT 
      1
  ) AS first_creatinine_on_icu, 
  (
    SELECT 
      (laboratory.Offset / 3600) as o 
    FROM 
      laboratory 
    WHERE 
      laboratory.CaseID = cases.CaseID 
      AND laboratory.LaboratoryID = 367 
      AND Offset >= ICUOffset 
    ORDER BY 
      laboratory.Offset ASC 
    LIMIT 
      1
  ) AS first_creatinine_on_icu_hours_from_pdms_admission, 
  (
    SELECT 
      (
        (laboratory.Offset - ICUOffset)/ 3600
      ) as o 
    FROM 
      laboratory 
    WHERE 
      laboratory.CaseID = cases.CaseID 
      AND laboratory.LaboratoryID = 367 
      AND Offset >= ICUOffset 
    ORDER BY 
      laboratory.Offset ASC 
    LIMIT 
      1
  ) AS first_creatinine_on_icu_hours_from_icu_admission 
FROM 
  cases 
