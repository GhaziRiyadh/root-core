using RootCore.Database;

namespace SampleWebApi.Models
{
    /// <summary>
    /// Sample Product entity demonstrating RootCore usage.
    /// </summary>
    public class Product : BaseModel
    {
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public decimal Price { get; set; }
        public int Stock { get; set; }
    }
}
