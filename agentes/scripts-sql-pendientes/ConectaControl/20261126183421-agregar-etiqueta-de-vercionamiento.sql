-- Pendiente de revisión humana. El agente NO lo ejecuta.
-- Proyecto: ConectaControl. Esquema CCIA. Clave no secreta.
-- Revisa CCIA.spSaveConfiguracionSistema antes de correr esto a mano.

IF NOT EXISTS (SELECT 1 FROM CCIA.ConfiguracionSistema WHERE vchClave = N'app.version')
    INSERT INTO CCIA.ConfiguracionSistema
        (vchClave, vchCategoria, vchNombre, vchDescripcion, vchTipo, nvchValor, bSecreto, iOrden, dtFecha)
    VALUES
        (N'app.version', N'App', N'Versión publicada', N'Semver visible en la barra. No es un secreto.', N'string', N'1.0.0', 0, 1, SYSUTCDATETIME());
