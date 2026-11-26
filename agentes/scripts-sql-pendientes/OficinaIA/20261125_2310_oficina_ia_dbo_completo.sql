-- ==========================================================================================
-- PROYECTO: OficinaIA — Sede Virtual Top-Down 2D & Orquestación Autónoma Cloud/Azure
-- ESQUEMA:  [dbo] (Prefijo limpio Ofia_ / spGetOfia* / spSaveOfia*)
-- ARCHIVO:  20261125_2310_oficina_ia_dbo_completo.sql
-- NOTA:     SCRIPT PENDIENTE DE REVISIÓN Y EJECUCIÓN MANUAL POR ALAN (NO EJECUTADO POR IA)
-- ==========================================================================================

SET NOCOUNT ON;
GO

-- 1. Configuración Global de la Oficina y Credenciales / Correo del Patrón
IF OBJECT_ID('[dbo].[Ofia_Configuracion]', 'U') IS NULL
BEGIN
    CREATE TABLE [dbo].[Ofia_Configuracion] (
        iIdConfiguracion       INT IDENTITY(1,1) PRIMARY KEY,
        nvchEmailPatron        NVARCHAR(250) NOT NULL DEFAULT N'',
        nvchNombrePatron       NVARCHAR(150) NOT NULL DEFAULT N'Alan (El Patrón)',
        nvchUrlPublicaAzure    NVARCHAR(300) NOT NULL DEFAULT N'http://localhost:5180',
        bPatrullaGlobalActiva  BIT           NOT NULL DEFAULT 1,
        vchBridgeSharedKeyHash VARCHAR(128)  NULL,
        dtUltimaConexionBridge DATETIME2     NULL,
        nvchHostBridge         NVARCHAR(150) NULL,
        dtActualizacion        DATETIME2     NOT NULL DEFAULT SYSDATETIME()
    );

    INSERT INTO [dbo].[Ofia_Configuracion] (nvchEmailPatron, nvchNombrePatron, nvchUrlPublicaAzure, bPatrullaGlobalActiva)
    VALUES (N'', N'Alan (El Patrón)', N'http://localhost:5180', 1);
END
GO

-- 2. Estado en Tiempo Real de cada Agente ("Monito" en la Oficina 2D)
IF OBJECT_ID('[dbo].[Ofia_AgenteEstado]', 'U') IS NULL
BEGIN
    CREATE TABLE [dbo].[Ofia_AgenteEstado] (
        iIdAgente                 INT IDENTITY(1,1) PRIMARY KEY,
        vchCodigoAgente           VARCHAR(60)   NOT NULL UNIQUE,
        nvchNombreMostrar         NVARCHAR(100) NOT NULL,
        nvchRolCorto              NVARCHAR(120) NOT NULL,
        vchColorAvatar            VARCHAR(20)   NOT NULL DEFAULT '#3B82F6',
        nvchProyectoObjetivo      NVARCHAR(100) NOT NULL,
        nvchRutaRepositorio       NVARCHAR(300) NOT NULL,
        vchEsquemaObjetivo        VARCHAR(20)   NULL,
        vchZonaActual             VARCHAR(40)   NOT NULL DEFAULT 'CUBICULO', -- CUBICULO, SALA_JUNTAS, SERVIDORES_SQL, OFICINA_PATRON, WORKTREE_LAB, CAFETERIA
        iCubiculoX                INT           NOT NULL DEFAULT 180,
        iCubiculoY                INT           NOT NULL DEFAULT 180,
        iPosX                     INT           NOT NULL DEFAULT 180,
        iPosY                     INT           NOT NULL DEFAULT 180,
        vchEstadoAnimacion        VARCHAR(40)   NOT NULL DEFAULT 'TYPING',   -- IDLE, WALKING, TYPING, READING_DB, MEETING, WAITING_APPROVAL, BUILDING
        nvchPensamientoActual     NVARCHAR(500) NOT NULL DEFAULT N'Vigilando arquitectura y módulos...',
        bAutonomoActivo           BIT           NOT NULL DEFAULT 1,
        iMinutosIntervaloPatrulla INT           NOT NULL DEFAULT 30,
        iPresupuestoTokensDiario  INT           NOT NULL DEFAULT 150000,
        iTokensConsumidosHoy      INT           NOT NULL DEFAULT 0,
        vchUltimoCommitEscaneado  VARCHAR(64)   NULL,
        dtUltimaPatrulla          DATETIME2     NULL,
        dtUltimoLatido            DATETIME2     NOT NULL DEFAULT SYSDATETIME()
    );

    INSERT INTO [dbo].[Ofia_AgenteEstado]
        (vchCodigoAgente, nvchNombreMostrar, nvchRolCorto, vchColorAvatar, nvchProyectoObjetivo, nvchRutaRepositorio, vchEsquemaObjetivo, iCubiculoX, iCubiculoY, iPosX, iPosY, nvchPensamientoActual)
    VALUES
        ('agente-estratega-ia',    N'Estratega IA',     N'Arquitecto Principal & UX', '#F59E0B', N'Transversal',                   N'D:\Proyectos',                              NULL,   550, 210, 550, 210, N'Investigando mejores prácticas SaaS y seguridad...'),
        ('agente-geoconecta',      N'Ing. GeoConecta',  N'Telemetría GPS & Flotillas','#10B981', N'GeoConecta',                    N'D:\Proyectos\GeoConecta',                   'GCIA', 170, 210, 170, 210, N'Auditando multi-tenancy y SPs en esquema GCIA...'),
        ('agente-conectanegocios', N'Ing. Negocios',    N'Multi-Cliente .NET 9',      '#3B82F6', N'ConectaNegocios',               N'D:\Proyectos\ConectaNegocios',              'CNIA', 170, 360, 170, 360, N'Revisando contratos entre API y 5 clientes en CNIA...'),
        ('agente-conectalanding',  N'Esp. Landing CRO', N'Marketing, SEO & Web',      '#EC4899', N'Repo Conecta Negocios Landing', N'D:\Proyectos\Repo Conecta Negocios Landing',NULL,   170, 510, 170, 510, N'Analizando velocidad web, SEO y conversión...'),
        ('agente-santiagoia',      N'Ing. SantiagoIA',  N'Gobierno Digital & IA',     '#8B5CF6', N'SANTIAGOIA',                    N'D:\Proyectos\SANTIAGOIA',                   'SCIA', 930, 210, 930, 210, N'Inspeccionando trámites, scrapers y esquema SCIA...'),
        ('agente-qa-e2e',          N'Inspector QA E2E', N'Playwright & e2e-admin',    '#EF4444', N'Test Proyecto',                 N'D:\Proyectos\Test Proyecto',                NULL,   930, 360, 930, 360, N'Verificando cobertura de suites Playwright...');
END
GO

-- 3. Propuestas, Vulnerabilidades y Planes Maestros Enviados al Patrón
IF OBJECT_ID('[dbo].[Ofia_Propuesta]', 'U') IS NULL
BEGIN
    CREATE TABLE [dbo].[Ofia_Propuesta] (
        iIdPropuesta              INT IDENTITY(1,1) PRIMARY KEY,
        vchFolio                  VARCHAR(30)    NOT NULL UNIQUE,
        iIdAgenteAutor            INT            NOT NULL FOREIGN KEY REFERENCES [dbo].[Ofia_AgenteEstado](iIdAgente),
        bValidadoPorEstratega     BIT            NOT NULL DEFAULT 1,
        nvchProyecto              NVARCHAR(100)  NOT NULL,
        vchCategoria              VARCHAR(40)    NOT NULL, -- VULNERABILIDAD, SQL_TUNING, BUG_POTENCIAL, MEJORA_PRO
        vchSeveridad              VARCHAR(20)    NOT NULL, -- CRITICA, ALTA, MEDIA, BAJA
        nvchTitulo                NVARCHAR(250)  NOT NULL,
        nvchResumenEjecutivo      NVARCHAR(2000) NOT NULL,
        nvchPlanMaestroMarkdown   NVARCHAR(MAX)  NOT NULL,
        nvchRutaArchivoPlan       NVARCHAR(400)  NOT NULL DEFAULT N'',
        vchHuellaDeduplicacion    VARCHAR(64)    NOT NULL,
        vchEstatus                VARCHAR(40)    NOT NULL DEFAULT 'PENDIENTE_FIRMA_PATRON',
        nvchNotaPatron            NVARCHAR(1000) NULL,
        vchRamaGit                VARCHAR(150)   NULL,
        nvchRutaWorktree          NVARCHAR(400)  NULL,
        nvchRutaScriptSqlPendiente NVARCHAR(400) NULL,
        bCompilacionExitosa       BIT            NULL,
        nvchResumenEjecucion      NVARCHAR(MAX)  NULL,
        dtCreacion                DATETIME2      NOT NULL DEFAULT SYSDATETIME(),
        dtEnvioCorreo             DATETIME2      NULL,
        dtDecisionPatron          DATETIME2      NULL,
        dtFinEjecucion            DATETIME2      NULL
    );

    CREATE INDEX IX_Ofia_Propuesta_Deduplicacion
        ON [dbo].[Ofia_Propuesta](vchHuellaDeduplicacion)
        INCLUDE (vchEstatus);

    CREATE INDEX IX_Ofia_Propuesta_Estatus
        ON [dbo].[Ofia_Propuesta](vchEstatus, vchSeveridad, dtCreacion DESC)
        INCLUDE (nvchTitulo, nvchProyecto, iIdAgenteAutor);
END
GO

-- 4. Tokens Firmados para Aprobación en 1 Clic desde el Correo del Patrón
IF OBJECT_ID('[dbo].[Ofia_TokenCorreo]', 'U') IS NULL
BEGIN
    CREATE TABLE [dbo].[Ofia_TokenCorreo] (
        iIdToken          INT IDENTITY(1,1) PRIMARY KEY,
        iIdPropuesta      INT          NOT NULL FOREIGN KEY REFERENCES [dbo].[Ofia_Propuesta](iIdPropuesta),
        vchTokenHash      VARCHAR(64)  NOT NULL UNIQUE,
        dtExpiracion      DATETIME2    NOT NULL,
        bUsado            BIT          NOT NULL DEFAULT 0,
        dtUso             DATETIME2    NULL,
        vchAccionAplicada VARCHAR(30)  NULL
    );
END
GO

-- 5. Bitácora en Vivo de Eventos y Globos de Diálogo de la Oficina
IF OBJECT_ID('[dbo].[Ofia_BitacoraEvento]', 'U') IS NULL
BEGIN
    CREATE TABLE [dbo].[Ofia_BitacoraEvento] (
        iIdEvento          BIGINT IDENTITY(1,1) PRIMARY KEY,
        iIdAgente          INT           NOT NULL FOREIGN KEY REFERENCES [dbo].[Ofia_AgenteEstado](iIdAgente),
        iIdPropuesta       INT           NULL FOREIGN KEY REFERENCES [dbo].[Ofia_Propuesta](iIdPropuesta),
        vchTipoEvento      VARCHAR(40)   NOT NULL,
        nvchMensajeCorto   NVARCHAR(300) NOT NULL,
        nvchDetalleTecnico NVARCHAR(MAX) NULL,
        dtFecha            DATETIME2     NOT NULL DEFAULT SYSDATETIME()
    );
END
GO

-- ==========================================================================================
-- STORED PROCEDURES EN [dbo] (Estándar EngramaCoreStandar: bResult + vchMessage)
-- ==========================================================================================

-- SP 1: Obtener Configuración Global de la Oficina
CREATE OR ALTER PROCEDURE [dbo].[spGetOfiaConfiguracion]
AS
BEGIN
    SET NOCOUNT ON;
    SELECT TOP 1
        CAST(1 AS BIT) AS bResult,
        N'' AS vchMessage,
        iIdConfiguracion,
        nvchEmailPatron,
        nvchNombrePatron,
        nvchUrlPublicaAzure,
        bPatrullaGlobalActiva,
        dtUltimaConexionBridge,
        ISNULL(nvchHostBridge, N'') AS nvchHostBridge,
        dtActualizacion
    FROM [dbo].[Ofia_Configuracion] WITH(NOLOCK)
    ORDER BY iIdConfiguracion ASC;
END
GO

-- SP 2: Guardar Configuración Global (Correo del Patrón / URL Azure / Pausa Global)
CREATE OR ALTER PROCEDURE [dbo].[spSaveOfiaConfiguracion]
    @nvchEmailPatron       NVARCHAR(250),
    @nvchNombrePatron      NVARCHAR(150),
    @nvchUrlPublicaAzure   NVARCHAR(300),
    @bPatrullaGlobalActiva BIT
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRY
        UPDATE [dbo].[Ofia_Configuracion]
        SET nvchEmailPatron       = ISNULL(@nvchEmailPatron, N''),
            nvchNombrePatron      = ISNULL(NULLIF(@nvchNombrePatron, N''), N'Alan (El Patrón)'),
            nvchUrlPublicaAzure   = ISNULL(NULLIF(@nvchUrlPublicaAzure, N''), N'http://localhost:5180'),
            bPatrullaGlobalActiva = @bPatrullaGlobalActiva,
            dtActualizacion       = SYSDATETIME();

        SELECT
            CAST(1 AS BIT) AS bResult,
            N'Configuración de OficinaIA guardada correctamente.' AS vchMessage;
    END TRY
    BEGIN CATCH
        SELECT CAST(0 AS BIT) AS bResult, ERROR_MESSAGE() AS vchMessage;
    END CATCH
END
GO

-- SP 3: Obtener todos los Agentes y su posición/estado en tiempo real
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
        ISNULL(vchUltimoCommitEscaneado, '') AS vchUltimoCommitEscaneado,
        dtUltimaPatrulla,
        dtUltimoLatido
    FROM [dbo].[Ofia_AgenteEstado] WITH(NOLOCK)
    ORDER BY iIdAgente ASC;
END
GO

-- SP 4: Actualizar posición, pensamiento o configuración de un Agente
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
    @bActualizarPatrulla       BIT = 0
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

-- SP 5: Consultar Propuestas / Planes Maestros (para el Escritorio del Patrón y Cola Bridge)
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

-- SP 6: Registrar Nueva Propuesta + Token de Aprobación por Correo (con anti-duplicados SHA-256)
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
        IF EXISTS (
            SELECT 1 FROM [dbo].[Ofia_Propuesta] WITH(NOLOCK)
            WHERE vchHuellaDeduplicacion = @vchHuellaDeduplicacion
              AND vchEstatus NOT IN ('RECHAZADO', 'APLICADO_MERGE')
        )
        BEGIN
            SELECT
                CAST(0 AS BIT) AS bResult,
                N'Hallazgo duplicado omitido (ya existe propuesta activa).' AS vchMessage,
                0 AS iIdPropuesta,
                '' AS vchFolio;
            RETURN;
        END

        DECLARE @iIdAgente INT = (SELECT TOP 1 iIdAgente FROM [dbo].[Ofia_AgenteEstado] WHERE vchCodigoAgente = @vchCodigoAgente);
        IF @iIdAgente IS NULL SET @iIdAgente = 1;

        BEGIN TRAN;

        DECLARE @iNext INT = ISNULL((SELECT MAX(iIdPropuesta) FROM [dbo].[Ofia_Propuesta]), 0) + 1;
        DECLARE @vchFolio VARCHAR(30) = CONCAT('OFIA-', FORMAT(SYSDATETIME(), 'yyyyMMdd'), '-', RIGHT('0000' + CAST(@iNext AS VARCHAR(10)), 4));

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
            N'Propuesta registrada y enviada al escritorio del Patrón.' AS vchMessage,
            @iIdNueva AS iIdPropuesta,
            @vchFolio AS vchFolio;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRAN;
        SELECT CAST(0 AS BIT) AS bResult, ERROR_MESSAGE() AS vchMessage, 0 AS iIdPropuesta, '' AS vchFolio;
    END CATCH
END
GO

-- SP 7: Decisión Idempotente del Patrón (Desde el Correo o desde la Oficina en Azure)
CREATE OR ALTER PROCEDURE [dbo].[spSaveOfiaDecisionPatron]
    @iIdPropuesta   INT = 0,
    @vchDecision    VARCHAR(30), -- 'APROBADO_EN_COLA' | 'RECHAZADO' | 'POSPUESTO'
    @nvchNotaPatron NVARCHAR(1000) = N'',
    @vchTokenHash   VARCHAR(64) = ''
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRY
        BEGIN TRAN;

        IF LEN(ISNULL(@vchTokenHash, '')) > 0
        BEGIN
            SELECT TOP 1 @iIdPropuesta = iIdPropuesta
            FROM [dbo].[Ofia_TokenCorreo] WITH(UPDLOCK, ROWLOCK)
            WHERE vchTokenHash = @vchTokenHash AND bUsado = 0 AND dtExpiracion > SYSDATETIME();

            IF ISNULL(@iIdPropuesta, 0) <= 0
            BEGIN
                ROLLBACK TRAN;
                SELECT CAST(0 AS BIT) AS bResult, N'Este enlace de aprobación ya fue procesado anteriormente o expiró.' AS vchMessage, 0 AS iIdPropuesta;
                RETURN;
            END

            UPDATE [dbo].[Ofia_TokenCorreo]
            SET bUsado = 1, dtUso = SYSDATETIME(), vchAccionAplicada = @vchDecision
            WHERE vchTokenHash = @vchTokenHash;
        END

        IF NOT EXISTS (SELECT 1 FROM [dbo].[Ofia_Propuesta] WHERE iIdPropuesta = @iIdPropuesta)
        BEGIN
            ROLLBACK TRAN;
            SELECT CAST(0 AS BIT) AS bResult, N'No se encontró la propuesta indicada.' AS vchMessage, 0 AS iIdPropuesta;
            RETURN;
        END

        UPDATE [dbo].[Ofia_Propuesta]
        SET vchEstatus       = @vchDecision,
            nvchNotaPatron   = ISNULL(@nvchNotaPatron, N''),
            dtDecisionPatron = SYSDATETIME()
        WHERE iIdPropuesta = @iIdPropuesta;

        DECLARE @iIdAgente INT = (SELECT TOP 1 iIdAgenteAutor FROM [dbo].[Ofia_Propuesta] WHERE iIdPropuesta = @iIdPropuesta);
        INSERT INTO [dbo].[Ofia_BitacoraEvento] (iIdAgente, iIdPropuesta, vchTipoEvento, nvchMensajeCorto)
        VALUES (@iIdAgente, @iIdPropuesta, 'DECISION_PATRON', CONCAT(N'El Patrón dictaminó: ', @vchDecision));

        COMMIT TRAN;

        SELECT
            CAST(1 AS BIT) AS bResult,
            N'Decisión del Patrón aplicada correctamente.' AS vchMessage,
            @iIdPropuesta AS iIdPropuesta;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRAN;
        SELECT CAST(0 AS BIT) AS bResult, ERROR_MESSAGE() AS vchMessage, 0 AS iIdPropuesta;
    END CATCH
END
GO

-- SP 8: Reportar Progreso / Resultado de Compilación Worktree desde el Agente Ejecutor
CREATE OR ALTER PROCEDURE [dbo].[spSaveOfiaResultadoEjecucion]
    @iIdPropuesta              INT,
    @vchEstatus                VARCHAR(40), -- 'PROGRAMANDO_WORKTREE' | 'COMPILADO_LISTO' | 'ERROR_COMPILACION'
    @vchRamaGit                VARCHAR(150) = '',
    @nvchRutaWorktree          NVARCHAR(400) = N'',
    @nvchRutaScriptSqlPendiente NVARCHAR(400) = N'',
    @bCompilacionExitosa       BIT = 0,
    @nvchResumenEjecucion      NVARCHAR(MAX) = N''
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRY
        UPDATE [dbo].[Ofia_Propuesta]
        SET vchEstatus                 = @vchEstatus,
            vchRamaGit                 = CASE WHEN LEN(ISNULL(@vchRamaGit,'')) > 0 THEN @vchRamaGit ELSE vchRamaGit END,
            nvchRutaWorktree           = CASE WHEN LEN(ISNULL(@nvchRutaWorktree,N'')) > 0 THEN @nvchRutaWorktree ELSE nvchRutaWorktree END,
            nvchRutaScriptSqlPendiente = CASE WHEN LEN(ISNULL(@nvchRutaScriptSqlPendiente,N'')) > 0 THEN @nvchRutaScriptSqlPendiente ELSE nvchRutaScriptSqlPendiente END,
            bCompilacionExitosa        = @bCompilacionExitosa,
            nvchResumenEjecucion       = @nvchResumenEjecucion,
            dtFinEjecucion             = CASE WHEN @vchEstatus IN ('COMPILADO_LISTO', 'ERROR_COMPILACION') THEN SYSDATETIME() ELSE dtFinEjecucion END
        WHERE iIdPropuesta = @iIdPropuesta;

        SELECT CAST(1 AS BIT) AS bResult, N'Resultado de ejecución actualizado.' AS vchMessage;
    END TRY
    BEGIN CATCH
        SELECT CAST(0 AS BIT) AS bResult, ERROR_MESSAGE() AS vchMessage;
    END CATCH
END
GO

-- SP 9: Consultar Últimos Eventos de Bitácora en Vivo
CREATE OR ALTER PROCEDURE [dbo].[spGetOfiaEventosRecientes]
    @iTop INT = 40
AS
BEGIN
    SET NOCOUNT ON;
    SELECT TOP (@iTop)
        CAST(1 AS BIT) AS bResult,
        N'' AS vchMessage,
        e.iIdEvento,
        e.iIdAgente,
        a.vchCodigoAgente,
        a.nvchNombreMostrar AS nvchNombreAgente,
        a.vchColorAvatar,
        ISNULL(e.iIdPropuesta, 0) AS iIdPropuesta,
        e.vchTipoEvento,
        e.nvchMensajeCorto,
        e.dtFecha
    FROM [dbo].[Ofia_BitacoraEvento] e WITH(NOLOCK)
    INNER JOIN [dbo].[Ofia_AgenteEstado] a WITH(NOLOCK) ON e.iIdAgente = a.iIdAgente
    ORDER BY e.iIdEvento DESC;
END
GO


-- SP 10: Consultar Propuesta por Token de Correo en SOLO LECTURA (inmune a bots de Gmail/Outlook en GET)
CREATE OR ALTER PROCEDURE [dbo].[spGetOfiaPropuestaPorToken]
    @vchTokenHash VARCHAR(64)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT TOP 1
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
        p.vchEstatus,
        ISNULL(p.nvchNotaPatron, N'') AS nvchNotaPatron,
        ISNULL(p.vchRamaGit, '') AS vchRamaGit,
        ISNULL(p.nvchRutaScriptSqlPendiente, N'') AS nvchRutaScriptSqlPendiente,
        ISNULL(p.bCompilacionExitosa, 0) AS bCompilacionExitosa,
        ISNULL(p.nvchResumenEjecucion, N'') AS nvchResumenEjecucion,
        p.dtCreacion,
        p.dtDecisionPatron,
        p.dtFinEjecucion,
        t.bUsado AS bTokenYaUsado,
        CAST(CASE WHEN t.dtExpiracion > SYSDATETIME() THEN 0 ELSE 1 END AS BIT) AS bTokenExpirado
    FROM [dbo].[Ofia_TokenCorreo] t WITH(NOLOCK)
    INNER JOIN [dbo].[Ofia_Propuesta] p WITH(NOLOCK) ON t.iIdPropuesta = p.iIdPropuesta
    INNER JOIN [dbo].[Ofia_AgenteEstado] a WITH(NOLOCK) ON p.iIdAgenteAutor = a.iIdAgente
    WHERE t.vchTokenHash = @vchTokenHash;
END
GO

-- SP 11: Reclamo Atómico de Tarea Aprobada desde el Puente Local de la PC de Alan
CREATE OR ALTER PROCEDURE [dbo].[spSaveOfiaReclamarTrabajoLocal]
    @nvchHostBridge NVARCHAR(150)
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRY
        DECLARE @Claimed TABLE (iIdPropuesta INT);

        UPDATE TOP (1) p
        SET p.vchEstatus = 'PROGRAMANDO_WORKTREE'
        OUTPUT INSERTED.iIdPropuesta INTO @Claimed(iIdPropuesta)
        FROM [dbo].[Ofia_Propuesta] p WITH(UPDLOCK, READPAST)
        WHERE p.vchEstatus = 'APROBADO_EN_COLA';

        UPDATE [dbo].[Ofia_Configuracion]
        SET dtUltimaConexionBridge = SYSDATETIME(),
            nvchHostBridge = ISNULL(@nvchHostBridge, N'PC-Local-Alan');

        IF NOT EXISTS (SELECT 1 FROM @Claimed)
        BEGIN
            SELECT CAST(0 AS BIT) AS bResult, N'Sin trabajos pendientes en cola.' AS vchMessage, 0 AS iIdPropuesta;
            RETURN;
        END

        DECLARE @iId INT = (SELECT TOP 1 iIdPropuesta FROM @Claimed);

        SELECT TOP 1
            CAST(1 AS BIT) AS bResult,
            N'Trabajo reclamado por el Puente Local.' AS vchMessage,
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
            p.vchEstatus,
            ISNULL(p.nvchNotaPatron, N'') AS nvchNotaPatron,
            ISNULL(p.vchRamaGit, '') AS vchRamaGit,
            ISNULL(p.nvchRutaScriptSqlPendiente, N'') AS nvchRutaScriptSqlPendiente,
            ISNULL(p.bCompilacionExitosa, 0) AS bCompilacionExitosa,
            ISNULL(p.nvchResumenEjecucion, N'') AS nvchResumenEjecucion,
            p.dtCreacion,
            p.dtDecisionPatron,
            p.dtFinEjecucion
        FROM [dbo].[Ofia_Propuesta] p
        INNER JOIN [dbo].[Ofia_AgenteEstado] a ON p.iIdAgenteAutor = a.iIdAgente
        WHERE p.iIdPropuesta = @iId;
    END TRY
    BEGIN CATCH
        SELECT CAST(0 AS BIT) AS bResult, ERROR_MESSAGE() AS vchMessage, 0 AS iIdPropuesta;
    END CATCH
END
GO

-- SP 12: Latido (Heartbeat) del Puente Local conectado a Azure
CREATE OR ALTER PROCEDURE [dbo].[spSaveOfiaLatidoBridge]
    @nvchHostBridge NVARCHAR(150)
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE [dbo].[Ofia_Configuracion]
    SET dtUltimaConexionBridge = SYSDATETIME(),
        nvchHostBridge = ISNULL(@nvchHostBridge, N'PC-Local-Alan');

    SELECT CAST(1 AS BIT) AS bResult, N'Heartbeat registrado.' AS vchMessage;
END
GO
