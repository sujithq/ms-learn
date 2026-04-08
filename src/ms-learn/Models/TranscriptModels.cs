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

    [JsonPropertyName("certificationData")]
    public CertificationData? CertificationData { get; set; }

    // Convenience property to access active certifications
    [JsonIgnore]
    public IReadOnlyList<Certification> Certifications => CertificationData?.ActiveCertifications ?? new List<Certification>();
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

public class CertificationData
{
    [JsonPropertyName("mcid")]
    public string? Mcid { get; set; }

    [JsonPropertyName("legalName")]
    public string? LegalName { get; set; }

    [JsonPropertyName("totalActiveCertifications")]
    public int TotalActiveCertifications { get; set; }

    [JsonPropertyName("totalHistoricalCertifications")]
    public int TotalHistoricalCertifications { get; set; }

    [JsonPropertyName("totalExamsPassed")]
    public int TotalExamsPassed { get; set; }

    [JsonPropertyName("totalQualificationsEarned")]
    public int TotalQualificationsEarned { get; set; }

    [JsonPropertyName("activeCertifications")]
    public List<Certification> ActiveCertifications { get; set; } = [];

    [JsonPropertyName("historicalCertifications")]
    public List<Certification> HistoricalCertifications { get; set; } = [];
}

public class Certification
{
    [JsonPropertyName("name")]
    public string? Name { get; set; }

    // Convenience property to match existing usage of Title
    [JsonIgnore]
    public string? Title => Name;

    [JsonPropertyName("certificationNumber")]
    public string? CertificationNumber { get; set; }

    [JsonPropertyName("status")]
    public string? Status { get; set; }

    [JsonPropertyName("dateEarned")]
    public DateTime? DateEarned { get; set; }

    [JsonPropertyName("expiration")]
    public DateTime? Expiration { get; set; }

    // Convenience property to match existing usage of ExpirationDate
    [JsonIgnore]
    public DateTime? ExpirationDate => Expiration;

    // IconUrl is not in the API response, but keep for compatibility
    [JsonPropertyName("iconUrl")]
    public string? IconUrl { get; set; }

    // Uid is not in the API response, but keep for compatibility
    [JsonPropertyName("uid")]
    public string? Uid { get; set; }
}