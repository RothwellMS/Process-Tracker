SELECT 
    CAST(Ref AS NVARCHAR(MAX)) AS Ref,
    CAST([Item No] AS NVARCHAR(MAX)) AS [Item No],
    [NC#],
    [Field 1],
    [Field 2],
    CAST(Description AS NVARCHAR(MAX)) AS Description,
    [Area(m^2)(Metal)],
    [Area(m^2)(Ins)],
    Opreation,
    Date
FROM (
    SELECT 
        CAST(Ref AS NVARCHAR(MAX)) AS Ref,
        CAST([Item No] AS NVARCHAR(MAX)) AS [Item No],
        [NC#],
        [Field 1],
        [Field 2],
        CAST(Description AS NVARCHAR(MAX)) AS Description,
        [Area(m^2)(Metal)],
        [Area(m^2)(Ins)],
        Opreation,
        Date
    FROM LaserCutter
    UNION ALL
    SELECT 
        CAST(Ref AS NVARCHAR(MAX)) AS Ref,
        CAST([Item No] AS NVARCHAR(MAX)) AS [Item No],
        [NC#],
        [Field 1],
        [Field 2],
        CAST(Description AS NVARCHAR(MAX)) AS Description,
        [Area(m^2)(Metal)],
        [Area(m^2)(Ins)],
        Opreation,
        Date
    FROM Insulation
    UNION ALL
    SELECT 
        CAST(Ref AS NVARCHAR(MAX)) AS Ref,
        CAST([Item No] AS NVARCHAR(MAX)) AS [Item No],
        [NC#],
        [Field 1],
        [Field 2],
        CAST(Description AS NVARCHAR(MAX)) AS Description,
        [Area(m^2)(Metal)],
        [Area(m^2)(Ins)],
        Opreation,
        Date
    FROM KnockOut
    UNION ALL
    SELECT 
        CAST(Ref AS NVARCHAR(MAX)) AS Ref,
        CAST([Item No] AS NVARCHAR(MAX)) AS [Item No],
        [NC#],
        [Field 1],
        [Field 2],
        CAST(Description AS NVARCHAR(MAX)) AS Description,
        [Area(m^2)(Metal)],
        [Area(m^2)(Ins)],
        Opreation,
        Date
    FROM StraightLine
) AS UnifiedTable
WHERE Date >= '2024-07-01'
ORDER BY 
    Ref,
    [Item No],
    [NC#],
    [Date];
