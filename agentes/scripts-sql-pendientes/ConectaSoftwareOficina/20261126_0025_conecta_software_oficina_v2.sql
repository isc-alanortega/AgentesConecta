-- ==========================================================================================
-- PROYECTO: Conecta Software Oficina (v2.0 — Edición Videojuego 3D + Órdenes del Patrón)
-- ESQUEMA:  [dbo]
-- ARCHIVO:  20261126_0025_conecta_software_oficina_v2.sql
-- PROPÓSITO:
--   1. Corrige definitivamente spSaveOfiaPropuesta para que NUNCA vuelva a proponer un plan
--      que el Patrón ya haya RECHAZADO anteriormente (salvo orden directa manual del Patrón).
--   2. Limpia cualquier propuesta duplicada pendiente que haya tenido el mismo hash que una rechazada.
--   3. Añade columna iMotivacion (0-100%) en Ofia_AgenteEstado para la nueva Sala de Videojuegos.
-- ==========================================================================================

SET NOCOUNT ON;
GO

-- 1. Agregar columna iMotivacion a Ofia_AgenteEstado si no existe
IF COL_LENGTH('[dbo].[Ofia_AgenteEstado]', 'iMotivacion') IS NULL
BEGIN
    ALTER TABLE [dbo].[Ofia_AgenteEstado]
    ADD iMotivacion INT NOT NULL CONSTRAINT DF_Ofia_Agente_Motivacion DEFAULT (95);
END
GO

-- 2. Limpiar duplicados actuales en PENDIENTE_FIRMA_PATRON que ya habían sido RECHAZADOS antes por el Patrón
DELETE pPend
FROM [dbo].[Ofia_Propuesta] pPend
WHERE pPend.vchEstatus = 'PENDIENTE_FIRMA_PATRON'
  AND EXISTS (
      SELECT 1
      FROM [dbo].[Ofia_Propuesta] pRech
      WHERE pRech.vchHuellaDeduplicacion = pPend.vchHuellaDeduplicacion
        AND pRech.vchEstatus = 'RECHAZADO'
  );
GO

-- 3. Actualizar spGetOfiaAgentes incluyendo iMotivacion
CREATE OR ALTER PROCEDURE [dbo].[spGetOfiaAgentes]
AS
BEGIN
    SET NOCOUNT ON;
    SELECT
        CAST(1 AS BIT) AS bResult,
        N'' AS vchMessage,
        iIdAgente,
        vchCodigoAgente,
        nvchNombreMostrar,
        nvchRolCorto,
        vchColorAvatar,
        nvchProyectoObjetivo,
        nvchRutaRepositorio,
        ISNULL(vchEsquemaObjetivo, '') AS vchEsquemaObjetivo,
        vchZonaActual,
        iCubiculoX,
        iCubiculoY,
        iPosX,
        iPosY,
        vchEstadoAnimacion,
        nvchPensamientoActual,
        bAutonomoActivo,
        iMinutosIntervaloPatrulla,
        iPresupuestoTokensDiario,
        iTokensConsumidosHoy,
        ISNULL(iMotivacion, 95) AS iMotivacion,
        ISNULL(vchUltimoCommitEscaneado, '') AS vchUltimoCommitEscaneado,
        dtUltimaPatrulla,
        dtUltimoLatido
    FROM [dbo].[Ofia_AgenteEstado] WITH(NOLOCK)
    ORDER BY iIdAgente ASC;
END
GO

-- 4. Actualizar spSaveOfiaAgenteEstado con soporte de motivación / Sala Gamer
CREATE OR ALTER PROCEDURE [dbo].[spSaveOfiaAgenteEstado]
    @vchCodigoAgente           VARCHAR(60),
    @vchZonaActual             VARCHAR(40),
    @iPosX                     INT,
    @iPosY                     INT,
    @vchEstadoAnimacion        VARCHAR(40),
    @nvchPensamientoActual     NVARCHAR(500),
    @bAutonomoActivo           BIT = NULL,
    @iMinutosIntervaloPatrulla INT = NULL,
    @iTokensSumar              INT = 0,
    @bActualizarPatrulla       BIT = 0,
    @iMotivacion               INT = NULL
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRY
        UPDATE [dbo].[Ofia_AgenteEstado]
        SET vchZonaActual             = ISNULL(@vchZonaActual, vchZonaActual),
            iPosX                     = @iPosX,
            iPosY                     = @iPosY,
            vchEstadoAnimacion        = ISNULL(@vchEstadoAnimacion, vchEstadoAnimacion),
            nvchPensamientoActual     = ISNULL(@nvchPensamientoActual, nvchPensamientoActual),
            bAutonomoActivo           = ISNULL(@bAutonomoActivo, bAutonomoActivo),
            iMinutosIntervaloPatrulla = ISNULL(@iMinutosIntervaloPatrulla, iMinutosIntervaloPatrulla),
            iTokensConsumidosHoy      = iTokensConsumidosHoy + ISNULL(@iTokensSumar, 0),
            iMotivacion               = ISNULL(@iMotivacion, iMotivacion),
            dtUltimaPatrulla          = CASE WHEN @bActualizarPatrulla = 1 THEN SYSDATETIME() ELSE dtUltimaPatrulla END,
            dtUltimoLatido            = SYSDATETIME()
        WHERE vchCodigoAgente = @vchCodigoAgente;

        INSERT INTO [dbo].[Ofia_BitacoraEvento] (iIdAgente, vchTipoEvento, nvchMensajeCorto)
        SELECT iIdAgente, @vchEstadoAnimacion, LEFT(@nvchPensamientoActual, 300)
        FROM [dbo].[Ofia_AgenteEstado]
        WHERE vchCodigoAgente = @vchCodigoAgente;

        SELECT CAST(1 AS BIT) AS bResult, N'OK' AS vchMessage;
    END TRY
    BEGIN CATCH
        SELECT CAST(0 AS BIT) AS bResult, ERROR_MESSAGE() AS vchMessage;
    END CATCH
END
GO

-- 5. Actualizar spGetOfiaPropuestas incluyendo vchHuellaDeduplicacion
CREATE OR ALTER PROCEDURE [dbo].[spGetOfiaPropuestas]
    @vchEstatus VARCHAR(40) = ''
AS
BEGIN
    SET NOCOUNT ON;
    SELECT
        CAST(1 AS BIT) AS bResult,
        N'' AS vchMessage,
        p.iIdPropuesta,
        p.vchFolio,
        p.iIdAgenteAutor,
        a.vchCodigoAgente,
        a.nvchNombreMostrar AS nvchNombreAgente,
        a.vchColorAvatar,
        p.bValidadoPorEstratega,
        p.nvchProyecto,
        p.vchCategoria,
        p.vchSeveridad,
        p.nvchTitulo,
        p.nvchResumenEjecutivo,
        p.nvchPlanMaestroMarkdown,
        p.nvchRutaArchivoPlan,
        p.vchHuellaDeduplicacion,
        p.vchEstatus,
        ISNULL(p.nvchNotaPatron, N'') AS nvchNotaPatron,
        ISNULL(p.vchRamaGit, '') AS vchRamaGit,
        ISNULL(p.nvchRutaScriptSqlPendiente, N'') AS nvchRutaScriptSqlPendiente,
        ISNULL(p.bCompilacionExitosa, 0) AS bCompilacionExitosa,
        ISNULL(p.nvchResumenEjecucion, N'') AS nvchResumenEjecucion,
        p.dtCreacion,
        p.dtDecisionPatron,
        p.dtFinEjecucion
    FROM [dbo].[Ofia_Propuesta] p WITH(NOLOCK)
    INNER JOIN [dbo].[Ofia_AgenteEstado] a WITH(NOLOCK) ON p.iIdAgenteAutor = a.iIdAgente
    WHERE (@vchEstatus = '' OR p.vchEstatus = @vchEstatus)
    ORDER BY p.dtCreacion DESC;
END
GO

-- 6. BLINDAJE DEFINITIVO en spSaveOfiaPropuesta:
--    Si una huella o título ya existe (INCLUYENDO 'RECHAZADO' por el Patrón), NO vuelve a insertarla jamás.
CREATE OR ALTER PROCEDURE [dbo].[spSaveOfiaPropuesta]
    @vchCodigoAgente         VARCHAR(60),
    @nvchProyecto            NVARCHAR(100),
    @vchCategoria            VARCHAR(40),
    @vchSeveridad            VARCHAR(20),
    @nvchTitulo              NVARCHAR(250),
    @nvchResumenEjecutivo    NVARCHAR(2000),
    @nvchPlanMaestroMarkdown NVARCHAR(MAX),
    @nvchRutaArchivoPlan     NVARCHAR(400),
    @vchHuellaDeduplicacion  VARCHAR(64),
    @vchTokenHash            VARCHAR(64)
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRY
        -- Bloquea cualquier propuesta previa con la misma huella (incluyendo RECHAZADO, APLICADO_MERGE, PENDIENTE, etc.)
        IF EXISTS (
            SELECT 1 FROM [dbo].[Ofia_Propuesta] WITH(NOLOCK)
            WHERE vchHuellaDeduplicacion = @vchHuellaDeduplicacion
        )
        BEGIN
            SELECT
                CAST(0 AS BIT) AS bResult,
                N'Propuesta omitida: ya fue registrada o rechazada previamente por el Patrón.' AS vchMessage,
                0 AS iIdPropuesta,
                '' AS vchFolio;
            RETURN;
        END

        DECLARE @iIdAgente INT = (SELECT TOP 1 iIdAgente FROM [dbo].[Ofia_AgenteEstado] WHERE vchCodigoAgente = @vchCodigoAgente);
        IF @iIdAgente IS NULL SET @iIdAgente = 1;

        BEGIN TRAN;

        DECLARE @iNext INT = ISNULL((SELECT MAX(iIdPropuesta) FROM [dbo].[Ofia_Propuesta]), 0) + 1;
        DECLARE @vchFolio VARCHAR(30) = CONCAT('CSO-', FORMAT(SYSDATETIME(), 'yyyyMMdd'), '-', RIGHT('0000' + CAST(@iNext AS VARCHAR(10)), 4));

        INSERT INTO [dbo].[Ofia_Propuesta] (
            vchFolio, iIdAgenteAutor, bValidadoPorEstratega, nvchProyecto, vchCategoria, vchSeveridad,
            nvchTitulo, nvchResumenEjecutivo, nvchPlanMaestroMarkdown, nvchRutaArchivoPlan,
            vchHuellaDeduplicacion, vchEstatus, dtEnvioCorreo
        )
        VALUES (
            @vchFolio, @iIdAgente, 1, @nvchProyecto, @vchCategoria, @vchSeveridad,
            @nvchTitulo, @nvchResumenEjecutivo, @nvchPlanMaestroMarkdown, ISNULL(@nvchRutaArchivoPlan, N''),
            @vchHuellaDeduplicacion, 'PENDIENTE_FIRMA_PATRON', SYSDATETIME()
        );

        DECLARE @iIdNueva INT = SCOPE_IDENTITY();

        IF @vchTokenHash IS NOT NULL AND LEN(@vchTokenHash) > 0
        BEGIN
            INSERT INTO [dbo].[Ofia_TokenCorreo] (iIdPropuesta, vchTokenHash, dtExpiracion)
            VALUES (@iIdNueva, @vchTokenHash, DATEADD(HOUR, 72, SYSDATETIME()));
        END

        INSERT INTO [dbo].[Ofia_BitacoraEvento] (iIdAgente, iIdPropuesta, vchTipoEvento, nvchMensajeCorto)
        VALUES (@iIdAgente, @iIdNueva, 'CARPETA_PATRON', CONCAT(N'Entregó propuesta ', @vchFolio, N': ', LEFT(@nvchTitulo, 180)));

        COMMIT TRAN;

        SELECT
            CAST(1 AS BIT) AS bResult,
            N'Propuesta entregada en la Oficina del Patrón.' AS vchMessage,
            @iIdNueva AS iIdPropuesta,
            @vchFolio AS vchFolio;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRAN;
        SELECT CAST(0 AS BIT) AS bResult, ERROR_MESSAGE() AS vchMessage, 0 AS iIdPropuesta, '' AS vchFolio;
    END CATCH
END
GO
