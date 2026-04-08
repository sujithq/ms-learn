namespace MsLearn.Models;

using System.Text.Json.Serialization;

public class TranscriptData
{
    [JsonPropertyName("userName")]
    public string? UserName { get; set; }

    [JsonPropertyName("userDisplayName")]
    public string? UserDisplayName { get; set; }

    [JsonPropertyName("totalModulesCompleted")]
    public int TotalModulesCompleted { get; set; }

    [JsonPropertyName("totalTrainingMinutes")]
    public int TotalTrainingMinutes { get; set; }

    [JsonPropertyName("modulesCompleted")]
    public List<CompletedModule> ModulesCompleted { get; set; } = [];

    [JsonPropertyName("trophies")]
    public List<Trophy> Trophies { get; set; } = [];

    [JsonPropertyName("certifications")]
    public List<Certification> Certifications { get; set; } = [];
}

public class CompletedModule
{
    [JsonPropertyName("uid")]
    public string? Uid { get; set; }

    [JsonPropertyName("title")]
    public string? Title { get; set; }

    [JsonPropertyName("completionDate")]
    public DateTime? CompletionDate { get; set; }

    [JsonPropertyName("duration")]
    public int Duration { get; set; }

    [JsonPropertyName("xp")]
    public int Xp { get; set; }

    [JsonPropertyName("iconUrl")]
    public string? IconUrl { get; set; }

    [JsonPropertyName("locale")]
    public string? Locale { get; set; }

    [JsonPropertyName("roles")]
    public List<string> Roles { get; set; } = [];

    [JsonPropertyName("levels")]
    public List<string> Levels { get; set; } = [];

    [JsonPropertyName("products")]
    public List<string> Products { get; set; } = [];

    public string LearnUrl => $"https://learn.microsoft.com/en-us/training/modules/{Uid?.Split('.').LastOrDefault() ?? Uid}/";
}

public class Trophy
{
    [JsonPropertyName("uid")]
    public string? Uid { get; set; }

    [JsonPropertyName("title")]
    public string? Title { get; set; }

    [JsonPropertyName("iconUrl")]
    public string? IconUrl { get; set; }

    [JsonPropertyName("earnedDate")]
    public DateTime? EarnedDate { get; set; }
}

public class Certification
{
    [JsonPropertyName("uid")]
    public string? Uid { get; set; }

    [JsonPropertyName("title")]
    public string? Title { get; set; }

    [JsonPropertyName("certificationNumber")]
    public string? CertificationNumber { get; set; }

    [JsonPropertyName("dateEarned")]
    public DateTime? DateEarned { get; set; }

    [JsonPropertyName("expirationDate")]
    public DateTime? ExpirationDate { get; set; }

    [JsonPropertyName("iconUrl")]
    public string? IconUrl { get; set; }
}
