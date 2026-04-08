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
        catch
        {
            _transcript = null;
        }

        return _transcript;
    }
}
