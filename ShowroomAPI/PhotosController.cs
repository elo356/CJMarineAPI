using CloudinaryDotNet;
using CloudinaryDotNet.Actions;
using Microsoft.AspNetCore.Mvc;

[ApiController]
[Route("api/[controller]")]
public class PhotosController : ControllerBase
{
    private readonly Cloudinary _cloudinary;
    private static List<string> _photoUrls = new(); // en un proyecto real usarías DB

    public PhotosController(IConfiguration config)
    {
                var acc = new Account(
    Environment.GetEnvironmentVariable("CLOUDINARY_CLOUDNAME"),
    Environment.GetEnvironmentVariable("CLOUDINARY_APIKEY"),
    Environment.GetEnvironmentVariable("CLOUDINARY_APISECRET")
);

        _cloudinary = new Cloudinary(acc);
    }

    [HttpGet]
    public IActionResult GetPhotos() => Ok(_photoUrls);

    [HttpPost]
    public async Task<IActionResult> UploadPhoto(IFormFile file)
    {
        if (file == null || file.Length == 0) return BadRequest("No file uploaded");

        var uploadParams = new ImageUploadParams
        {
            File = new FileDescription(file.FileName, file.OpenReadStream())
        };
        var result = await _cloudinary.UploadAsync(uploadParams);

        _photoUrls.Add(result.SecureUrl.AbsoluteUri);
        return Ok(new { url = result.SecureUrl });
    }

    [HttpDelete]
    public IActionResult DeletePhoto([FromQuery] string url)
    {
        _photoUrls.Remove(url);
        return Ok("Deleted");
    }
}
