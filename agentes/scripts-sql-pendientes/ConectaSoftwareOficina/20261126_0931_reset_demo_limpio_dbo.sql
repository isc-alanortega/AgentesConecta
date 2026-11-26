-- ==========================================================================================
-- CONECTA SOFTWARE OFICINA — SCRIPT DE LIMPIEZA TOTAL PARA DEMO DESDE CERO ([dbo])
-- ARCHIVO: 20261126_0931_reset_demo_limpio_dbo.sql
-- QUÉ HACE:
--   1. Borra todas las propuestas/planes, tokens de correo y bitácora de eventos en Ofia_*.
--   2. Reinicia los contadores IDENTITY a 0 (para que el primer plan en la demo sea el #0001).
--   3. Regresa a los 6 agentes a sus cubículos iniciales con 100% de motivación y dtUltimaPatrulla = NULL
--      para que en cuanto arranques el proyecto frente a tu compañero comiencen a patrullar en vivo.
--   4. Conserva intacta tu configuración (tu correo de Patrón y nombre en Ofia_Configuracion)
--      y deja asegurada la mejora v2 (columna iMotivacion + no repetir rechazados).
-- NOTA: NO toca Test_Table ni ninguna tabla ajena a Ofia_*.
-- ==========================================================================================

SET NOCOUNT ON;
GO

-- 0. Asegurar columna iMotivacion (por si aún no se había corrido el script v2)
IF COL_LENGTH('[dbo].[Ofia_AgenteEstado]', 'iMotivacion') IS NULL
BEGIN
    ALTER TABLE [dbo].[Ofia_AgenteEstado]
    ADD iMotivacion INT NOT NULL CONSTRAINT DF_Ofia_Agente_Motivacion DEFAULT (100);
END
GO

BEGIN TRY
    BEGIN TRAN;

    -- 1. Limpiar tablas hijas primero (respetando Foreign Keys)
    IF OBJECT_ID('[dbo].[Ofia_TokenCorreo]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [dbo].[Ofia_TokenCorreo];
        DBCC CHECKIDENT ('[dbo].[Ofia_TokenCorreo]', RESEED, 0);
    END

    IF OBJECT_ID('[dbo].[Ofia_BitacoraEvento]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [dbo].[Ofia_BitacoraEvento];
        DBCC CHECKIDENT ('[dbo].[Ofia_BitacoraEvento]', RESEED, 0);
    END

    -- 2. Limpiar todos los planes / propuestas previas
    IF OBJECT_ID('[dbo].[Ofia_Propuesta]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [dbo].[Ofia_Propuesta];
        DBCC CHECKIDENT ('[dbo].[Ofia_Propuesta]', RESEED, 0);
    END

    -- 3. Reiniciar a los 6 Agentes IA en sus cubículos listos para arrancar desde cero
    IF OBJECT_ID('[dbo].[Ofia_AgenteEstado]', 'U') IS NOT NULL
    BEGIN
        UPDATE [dbo].[Ofia_AgenteEstado]
        SET vchZonaActual            = 'CUBICULO',
            iPosX                    = iCubiculoX,
            iPosY                    = iCubiculoY,
            vchEstadoAnimacion       = 'TYPING',
            nvchPensamientoActual    = CONCAT(N'Listo en estación para auditar ', nvchProyectoObjetivo, N'...'),
            bAutonomoActivo          = 1,
            iTokensConsumidosHoy     = 0,
            vchUltimoCommitEscaneado = NULL,
            dtUltimaPatrulla         = NULL,
            dtUltimoLatido           = SYSDATETIME();

        EXEC sp_executesql N'UPDATE [dbo].[Ofia_AgenteEstado] SET iMotivacion = 100;';
    END

    -- 4. Asegurar que la patrulla global esté encendida (conservando tu correo configurado)
    IF OBJECT_ID('[dbo].[Ofia_Configuracion]', 'U') IS NOT NULL
    BEGIN
        UPDATE [dbo].[Ofia_Configuracion]
        SET bPatrullaGlobalActiva = 1,
            dtActualizacion       = SYSDATETIME();
    END

    -- 5. Evento inicial limpio de apertura en el feed
    IF OBJECT_ID('[dbo].[Ofia_BitacoraEvento]', 'U') IS NOT NULL
       AND EXISTS (SELECT 1 FROM [dbo].[Ofia_AgenteEstado])
    BEGIN
        INSERT INTO [dbo].[Ofia_BitacoraEvento] (iIdAgente, vchTipoEvento, nvchMensajeCorto)
        SELECT TOP 1 iIdAgente, 'SISTEMA', N'🚀 Conecta Software Oficina iniciada desde cero. ¡Agentes listos para patrullar!'
        FROM [dbo].[Ofia_AgenteEstado]
        ORDER BY iIdAgente ASC;
    END

    COMMIT TRAN;
    PRINT '✅ Ambiente Ofia_* en [dbo] limpio al 100% y listo para la demostración.';
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0 ROLLBACK TRAN;
    THROW;
END CATCH
GO
