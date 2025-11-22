using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace RootCore.Database
{
    /// <summary>
    /// Base model with common fields for soft-delete support.
    /// </summary>
    public abstract class BaseModel
    {
        [Key]
        [DatabaseGenerated(DatabaseGeneratedOption.Identity)]
        public int Id { get; set; }

        public bool IsDeleted { get; set; } = false;

        // Uncomment if you want to add timestamp fields
        // public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
        // public DateTime? UpdatedAt { get; set; }
    }
}
