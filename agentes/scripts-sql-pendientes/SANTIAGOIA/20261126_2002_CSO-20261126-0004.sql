/*
===============================================================================
  Folio:       CSO-20261126-0004
  Proyecto:    SANTIAGOIA (SantiagoConectaIA)
  Esquema:     [SCIA]
  Objetivo:    Optimizar procedimientos almacenados agregando SET NOCOUNT ON
               para eliminar mensajes DONE_IN_PROC innecesarios en Dapper.
  SPs:         [SCIA].[spSaveCiudadanoCodigo]
               [SCIA].[spValidarCiudadanoCodigo]
  Fecha:       2026-11-26
  Nota:        Script idempotente (CREATE OR ALTER PROCEDURE).
               Revisar y ejecutar manualmente en SQL Server (solo lectura para agentes).
===============================================================================
*/

SET ANSI_NULLS ON;
GO
SET QUOTED_IDENTIFIER ON;
GO

CREATE OR ALTER PROCEDURE [SCIA].[spSaveCiudadanoCodigo]
(
    @vchTelefono VARCHAR(20),
    @vchCodigo VARCHAR(10)
)
AS
/*
** Propósito:       Generar/guardar código OTP para registro ciudadano.
** Actualizado por: agente-santiagoia (Folio CSO-20261126-0004)
** Última fecha:    26/11/2026
** Cambio:          Se agrega SET NOCOUNT ON para suprimir paquetes DONE_IN_PROC en Dapper.
*/
BEGIN
    SET NOCOUNT ON;

    DECLARE @vchError VARCHAR(200) = '';
    DECLARE @Telefono CHAR(10);

    DECLARE @Result AS TABLE
    (
        bResult BIT DEFAULT(1),
        vchMessage VARCHAR(500) DEFAULT('')
    );

    BEGIN TRY
        SET @vchTelefono = REPLACE(REPLACE(REPLACE(LTRIM(RTRIM(ISNULL(@vchTelefono, ''))), ' ', ''), '-', ''), '(', '');
        SET @vchTelefono = REPLACE(@vchTelefono, ')', '');
        SET @vchCodigo = LTRIM(RTRIM(ISNULL(@vchCodigo, '')));

        IF LEN(@vchTelefono) <> 10 OR @vchTelefono LIKE '%[^0-9]%'
        BEGIN
            SET @vchError = 'El teléfono debe tener exactamente 10 dígitos.';
            GOTO _FinCodigo;
        END

        IF LEFT(@vchTelefono, 1) IN ('0', '1')
        BEGIN
            SET @vchError = 'El teléfono debe iniciar con un dígito entre 2 y 9.';
            GOTO _FinCodigo;
        END

        IF @vchTelefono = REPLICATE(LEFT(@vchTelefono, 1), 10)
        BEGIN
            SET @vchError = 'El teléfono no puede tener todos los dígitos iguales.';
            GOTO _FinCodigo;
        END

        IF LEN(@vchCodigo) <> 6 OR @vchCodigo LIKE '%[^0-9]%'
        BEGIN
            SET @vchError = 'El código debe tener 6 dígitos.';
            GOTO _FinCodigo;
        END

        SET @Telefono = @vchTelefono;

        IF EXISTS (SELECT 1 FROM SCIA.Ciudadano C WITH (NOLOCK) WHERE C.vchTelefono = @Telefono)
        BEGIN
            SET @vchError = 'Este número ya está registrado.';
            GOTO _FinCodigo;
        END

        IF (
            SELECT COUNT(1)
            FROM SCIA.CiudadanoVerificacion CV WITH (NOLOCK)
            WHERE CV.vchTelefono = @Telefono
              AND CV.dtFechaCreacion >= DATEADD(HOUR, -1, GETDATE())
        ) >= 3
        BEGIN
            SET @vchError = 'Límite de envíos alcanzado. Intenta de nuevo en unos minutos.';
            GOTO _FinCodigo;
        END

        UPDATE SCIA.CiudadanoVerificacion
        SET dtExpiracion = DATEADD(MINUTE, -1, GETDATE())
        WHERE vchTelefono = @Telefono
          AND bValidado = 0
          AND dtExpiracion >= GETDATE();

        INSERT INTO SCIA.CiudadanoVerificacion
        (
            vchTelefono,
            vchCodigoHash,
            dtFechaCreacion,
            dtExpiracion,
            iIntentos,
            bValidado
        )
        VALUES
        (
            @Telefono,
            CONVERT(VARCHAR(500), HASHBYTES('SHA2_256', @vchCodigo), 2),
            GETDATE(),
            DATEADD(MINUTE, 10, GETDATE()),
            0,
            0
        );
    END TRY
    BEGIN CATCH
        SET @vchError = CONCAT(ERROR_PROCEDURE(), ': ', ERROR_MESSAGE(), ' - Línea ', ERROR_LINE());
    END CATCH

_FinCodigo:
    IF LEN(@vchError) > 0
        INSERT INTO @Result (bResult, vchMessage) VALUES (0, @vchError);
    ELSE
        INSERT INTO @Result (bResult, vchMessage) VALUES (1, 'Código generado.');

    SELECT TOP 1 * FROM @Result ORDER BY bResult DESC;
END
GO

SET ANSI_NULLS ON;
GO
SET QUOTED_IDENTIFIER ON;
GO

CREATE OR ALTER PROCEDURE [SCIA].[spValidarCiudadanoCodigo]
(
    @vchTelefono VARCHAR(20),
    @vchCodigo VARCHAR(10)
)
AS
/*
** Propósito:       Validar código OTP de ciudadano.
** Actualizado por: agente-santiagoia (Folio CSO-20261126-0004)
** Última fecha:    26/11/2026
** Cambio:          Se agrega SET NOCOUNT ON para suprimir paquetes DONE_IN_PROC en Dapper.
*/
BEGIN
    SET NOCOUNT ON;

    DECLARE @vchError VARCHAR(200) = '';
    DECLARE @Telefono CHAR(10);
    DECLARE @iIdCiudadanoVerificacion INT = 0;
    DECLARE @vchCodigoHash VARCHAR(500) = '';
    DECLARE @dtExpiracion DATETIME;
    DECLARE @iIntentos INT = 0;

    DECLARE @Result AS TABLE
    (
        bResult BIT DEFAULT(1),
        vchMessage VARCHAR(500) DEFAULT('')
    );

    BEGIN TRY
        SET @vchTelefono = REPLACE(REPLACE(REPLACE(LTRIM(RTRIM(ISNULL(@vchTelefono, ''))), ' ', ''), '-', ''), '(', '');
        SET @vchTelefono = REPLACE(@vchTelefono, ')', '');
        SET @vchCodigo = LTRIM(RTRIM(ISNULL(@vchCodigo, '')));

        IF LEN(@vchTelefono) <> 10 OR @vchTelefono LIKE '%[^0-9]%'
        BEGIN
            SET @vchError = 'El teléfono debe tener exactamente 10 dígitos.';
            GOTO _FinValidar;
        END

        IF LEN(@vchCodigo) <> 6 OR @vchCodigo LIKE '%[^0-9]%'
        BEGIN
            SET @vchError = 'El código debe tener 6 dígitos.';
            GOTO _FinValidar;
        END

        SET @Telefono = @vchTelefono;

        SELECT TOP 1
            @iIdCiudadanoVerificacion = CV.iIdCiudadanoVerificacion,
            @vchCodigoHash = CV.vchCodigoHash,
            @dtExpiracion = CV.dtExpiracion,
            @iIntentos = CV.iIntentos
        FROM SCIA.CiudadanoVerificacion CV WITH (NOLOCK)
        WHERE CV.vchTelefono = @Telefono
          AND CV.bValidado = 0
        ORDER BY CV.iIdCiudadanoVerificacion DESC;

        IF @iIdCiudadanoVerificacion <= 0
        BEGIN
            SET @vchError = 'Primero solicita un código.';
            GOTO _FinValidar;
        END

        IF @dtExpiracion < GETDATE()
        BEGIN
            SET @vchError = 'El código expiró. Solicita uno nuevo.';
            GOTO _FinValidar;
        END

        IF @iIntentos >= 5
        BEGIN
            SET @vchError = 'Demasiados intentos. Solicita un código nuevo.';
            GOTO _FinValidar;
        END

        IF @vchCodigoHash <> CONVERT(VARCHAR(500), HASHBYTES('SHA2_256', @vchCodigo), 2)
        BEGIN
            UPDATE SCIA.CiudadanoVerificacion
            SET iIntentos = iIntentos + 1
            WHERE iIdCiudadanoVerificacion = @iIdCiudadanoVerificacion;

            SET @vchError = 'Código incorrecto.';
            GOTO _FinValidar;
        END

        UPDATE SCIA.CiudadanoVerificacion
        SET bValidado = 1
        WHERE iIdCiudadanoVerificacion = @iIdCiudadanoVerificacion;
    END TRY
    BEGIN CATCH
        SET @vchError = CONCAT(ERROR_PROCEDURE(), ': ', ERROR_MESSAGE(), ' - Línea ', ERROR_LINE());
    END CATCH

_FinValidar:
    IF LEN(@vchError) > 0
        INSERT INTO @Result (bResult, vchMessage) VALUES (0, @vchError);
    ELSE
        INSERT INTO @Result (bResult, vchMessage) VALUES (1, 'Código validado.');

    SELECT TOP 1 * FROM @Result ORDER BY bResult DESC;
END
GO
