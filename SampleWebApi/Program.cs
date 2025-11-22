using Microsoft.EntityFrameworkCore;
using RootCore.Bases;
using RootCore.Configuration;
using SampleWebApi.Data;
using SampleWebApi.Models;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
// Configure AppSettings
builder.Services.Configure<AppSettings>(builder.Configuration.GetSection("AppSettings"));

// Add DbContext with SQLite
builder.Services.AddDbContext<ApplicationDbContext>(options =>
    options.UseSqlite(builder.Configuration.GetConnectionString("DefaultConnection") ?? "Data Source=sample.db"));

// Register RootCore services
builder.Services.AddScoped<BaseRepository<Product>>(sp => 
    new BaseRepository<Product>(sp.GetRequiredService<ApplicationDbContext>()));
builder.Services.AddScoped<BaseService<Product>>();

// Add controllers
builder.Services.AddControllers();

// Learn more about configuring OpenAPI at https://aka.ms/aspnet/openapi
builder.Services.AddOpenApi();

var app = builder.Build();

// Ensure database is created
using (var scope = app.Services.CreateScope())
{
    var context = scope.ServiceProvider.GetRequiredService<ApplicationDbContext>();
    context.Database.EnsureCreated();
}

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();
}

app.UseHttpsRedirection();

app.MapControllers();

app.Run();

