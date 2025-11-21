using Microsoft.AspNetCore.Mvc;
using RootCore.Bases;
using SampleWebApi.Models;

namespace SampleWebApi.Controllers
{
    /// <summary>
    /// Products API controller demonstrating RootCore usage.
    /// All CRUD endpoints are inherited from BaseController.
    /// </summary>
    [ApiController]
    [Route("api/[controller]")]
    public class ProductsController : BaseController<Product>
    {
        public ProductsController(BaseService<Product> service) : base(service)
        {
        }

        // All CRUD endpoints are inherited:
        // GET    /api/products           - Get paginated list
        // GET    /api/products/all       - Get all items
        // GET    /api/products/{id}      - Get by ID
        // POST   /api/products           - Create new
        // PUT    /api/products/{id}      - Update
        // DELETE /api/products/{id}      - Soft delete
        // POST   /api/products/{id}/restore - Restore
        // DELETE /api/products/{id}/force - Force delete
        // GET    /api/products/{id}/exists - Check exists
        // GET    /api/products/count     - Count items
        // POST   /api/products/bulk      - Bulk create
        // POST   /api/products/bulk-delete - Bulk delete

        // You can add custom endpoints here if needed
    }
}
