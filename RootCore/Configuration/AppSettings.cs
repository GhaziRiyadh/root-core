namespace RootCore.Configuration
{
    /// <summary>
    /// Permission actions for authorization.
    /// </summary>
    public enum PermissionAction
    {
        Create,
        Read,
        Update,
        Delete,
        ForceDelete,
        Restore,
        Logs,
        Manage,
        Copy,
        Export
    }

    /// <summary>
    /// Application settings configuration.
    /// </summary>
    public class AppSettings
    {
        public string DatabaseUri { get; set; } = "Data Source=database.db";
        public string SecretKey { get; set; } = "supersecretkey";
        public string Algorithm { get; set; } = "HS256";
        public int AccessTokenExpireMinutes { get; set; } = 30;
        public string ProjectName { get; set; } = "My ASP.NET Project";
        public string ProjectInfo { get; set; } = "My ASP.NET Project";
        public string ProjectVersion { get; set; } = "1.0.0";
        public string TimeZone { get; set; } = "Asia/Aden";
        public string UploadFolder { get; set; } = "uploads";
        public string StaticDir { get; set; } = "static";
    }
}
