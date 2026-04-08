namespace MsLearn.Services;

using System.Net.Http.Json;
using MsLearn.Models;

public class TranscriptService(HttpClient httpClient)
{
    private TranscriptData? _transcript;

    public async Task<TranscriptData?> GetTranscriptAsync()
    {
        if (_transcript is not null)
            return _transcript;

        try
        {
            _transcript = await httpClient.GetFromJsonAsync<TranscriptData>("data/transcript.json");
        }
        catch (HttpRequestException ex)
        {
            Console.Error.WriteLine($"Failed to fetch transcript: {ex.Message}");
        }
        catch (System.Text.Json.JsonException ex)
        {
            Console.Error.WriteLine($"Failed to parse transcript JSON: {ex.Message}");
        }

        return _transcript;
    }
}
