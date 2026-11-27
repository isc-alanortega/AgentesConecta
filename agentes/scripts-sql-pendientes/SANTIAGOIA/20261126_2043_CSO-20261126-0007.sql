/*
===============================================================================
  Folio:       CSO-20261126-0007
  Proyecto:    SANTIAGOIA (SantiagoConectaIA)
  Esquema:     [SCIA]
  Objetivo:    Crear índices no agrupados faltantes en columnas Foreign Key
               para acelerar JOINs, búsquedas por llave foránea y evitar
               bloqueos/escaneos en actualizaciones o eliminaciones padre.
  Índices:     1. [SCIA].[Catalogos].[IX_Catalogos_Id_Grupo]
                  (FK_Catalogos_Grupos -> [SCIA].[Grupos].[Id_Grupo])
               2. [SCIA].[CategoriaCatalogo].[IX_CategoriaCatalogo_iIdEmpresa]
                  (FK -> [SCIA].[Empresa].[iIdEmpresa])
               3. [SCIA].[ConfiguracionVisual].[IX_ConfiguracionVisual_iIdEmpresa]
                  (FK -> [SCIA].[Empresa].[iIdEmpresa])
  Autor:       agente-santiagoia
  Fecha:       2026-11-26
  Nota:        Script 100% idempotente (verifica existencia de tabla e índice).
               Revisar y ejecutar manualmente en SQL Server (BD solo lectura
               para agentes).
===============================================================================
*/

SET ANSI_NULLS ON;
GO
SET QUOTED_IDENTIFIER ON;
GO

/* ----------------------------------------------------------------------------
   1. [SCIA].[Catalogos] -> FK [Id_Grupo] -> [SCIA].[Grupos]([Id_Grupo])
   ---------------------------------------------------------------------------- */
IF OBJECT_ID(N'[SCIA].[Catalogos]', N'U') IS NOT NULL
   AND NOT EXISTS (
       SELECT 1
       FROM sys.indexes
       WHERE name = N'IX_Catalogos_Id_Grupo'
         AND object_id = OBJECT_ID(N'[SCIA].[Catalogos]')
   )
BEGIN
    CREATE NONCLUSTERED INDEX [IX_Catalogos_Id_Grupo]
        ON [SCIA].[Catalogos] ([Id_Grupo] ASC)
        INCLUDE ([Descripcion], [Valor]);

    PRINT N'Índice [IX_Catalogos_Id_Grupo] creado en [SCIA].[Catalogos].';
END
ELSE
BEGIN
    PRINT N'Índice [IX_Catalogos_Id_Grupo] omitido (ya existe o tabla no encontrada).';
END
GO

/* ----------------------------------------------------------------------------
   2. [SCIA].[CategoriaCatalogo] -> FK [iIdEmpresa] -> [SCIA].[Empresa]([iIdEmpresa])
   ---------------------------------------------------------------------------- */
IF OBJECT_ID(N'[SCIA].[CategoriaCatalogo]', N'U') IS NOT NULL
   AND NOT EXISTS (
       SELECT 1
       FROM sys.indexes
       WHERE name = N'IX_CategoriaCatalogo_iIdEmpresa'
         AND object_id = OBJECT_ID(N'[SCIA].[CategoriaCatalogo]')
   )
BEGIN
    CREATE NONCLUSTERED INDEX [IX_CategoriaCatalogo_iIdEmpresa]
        ON [SCIA].[CategoriaCatalogo] ([iIdEmpresa] ASC)
        INCLUDE ([vchNombre], [iOrdenAparicion]);

    PRINT N'Índice [IX_CategoriaCatalogo_iIdEmpresa] creado en [SCIA].[CategoriaCatalogo].';
END
ELSE
BEGIN
    PRINT N'Índice [IX_CategoriaCatalogo_iIdEmpresa] omitido (ya existe o tabla no encontrada).';
END
GO

/* ----------------------------------------------------------------------------
   3. [SCIA].[ConfiguracionVisual] -> FK [iIdEmpresa] -> [SCIA].[Empresa]([iIdEmpresa])
   ---------------------------------------------------------------------------- */
IF OBJECT_ID(N'[SCIA].[ConfiguracionVisual]', N'U') IS NOT NULL
   AND NOT EXISTS (
       SELECT 1
       FROM sys.indexes
       WHERE name = N'IX_ConfiguracionVisual_iIdEmpresa'
         AND object_id = OBJECT_ID(N'[SCIA].[ConfiguracionVisual]')
   )
BEGIN
    CREATE NONCLUSTERED INDEX [IX_ConfiguracionVisual_iIdEmpresa]
        ON [SCIA].[ConfiguracionVisual] ([iIdEmpresa] ASC);

    PRINT N'Índice [IX_ConfiguracionVisual_iIdEmpresa] creado en [SCIA].[ConfiguracionVisual].';
END
ELSE
BEGIN
    PRINT N'Índice [IX_ConfiguracionVisual_iIdEmpresa] omitido (ya existe o tabla no encontrada).';
END
GO
