"""
Job Search Automation CLI

Beautiful command-line interface for job description parsing and management.
"""

import os
import sys
import click
import json
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax
from rich import print as rprint

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.integrations.supabase.job_service import JobDatabaseService
from src.core.job_parser import JobDescriptionParser

console = Console()

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """
    🚀 Job Search Automation Platform
    
    Intelligent job description parsing and management system.
    """
    pass

@cli.command()
@click.option('--url', '-u', help='Job posting URL to parse')
@click.option('--text', '-t', help='Raw job description text')
@click.option('--file', '-f', help='File containing job description')
@click.option('--save/--no-save', default=True, help='Save to database')
@click.option('--validate/--no-validate', default=True, help='Validate parsed data')
def parse(url: Optional[str], text: Optional[str], file: Optional[str], save: bool, validate: bool):
    """Parse job description from URL, text, or file."""
    
    if not any([url, text, file]):
        console.print("❌ Please provide a URL, text, or file to parse", style="red")
        return
    
    if sum(bool(x) for x in [url, text, file]) > 1:
        console.print("❌ Please provide only one input source", style="red")
        return
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            
            if url:
                task = progress.add_task("🌐 Parsing job from URL...", total=None)
                if save:
                    service = JobDatabaseService()
                    result = service.process_job_from_url(url)
                else:
                    parser = JobDescriptionParser()
                    job_details = parser.parse_from_url(url)
                    result = {"status": "success", "parsed_data": job_details}
                    
            elif text:
                task = progress.add_task("📝 Parsing job from text...", total=None)
                if save:
                    service = JobDatabaseService()
                    result = service.process_job_from_text(text)
                else:
                    parser = JobDescriptionParser()
                    job_details = parser.parse_from_text(text)
                    result = {"status": "success", "parsed_data": job_details}
                    
            elif file:
                task = progress.add_task("📄 Parsing job from file...", total=None)
                with open(file, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                if save:
                    service = JobDatabaseService()
                    result = service.process_job_from_text(file_content)
                else:
                    parser = JobDescriptionParser()
                    job_details = parser.parse_from_text(file_content)
                    result = {"status": "success", "parsed_data": job_details}
            
            progress.remove_task(task)
        
        if result["status"] == "success":
            console.print("✅ Job parsed successfully!", style="green bold")
            
            if save:
                # Display database result
                _display_job_result(result)
            else:
                # Display parsed job details
                _display_job_details(result["parsed_data"])
            
            if validate and "validation" in result:
                _display_validation_results(result["validation"])
                
        else:
            console.print(f"❌ Parsing failed: {result['message']}", style="red")
            
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")

@cli.command()
@click.option('--company', '-c', help='Filter by company name')
@click.option('--skills', '-s', help='Filter by skills (comma-separated)')
@click.option('--location', '-l', help='Filter by location')
@click.option('--job-type', '-t', help='Filter by job type')
@click.option('--limit', default=20, help='Maximum results to return')
@click.option('--format', 'output_format', default='table', 
              type=click.Choice(['table', 'json', 'summary']),
              help='Output format')
def search(company: Optional[str], skills: Optional[str], location: Optional[str], 
          job_type: Optional[str], limit: int, output_format: str):
    """Search for jobs in the database."""
    
    try:
        service = JobDatabaseService()
        
        # Parse skills
        skills_list = [s.strip() for s in skills.split(',')] if skills else None
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("🔍 Searching jobs...", total=None)
            
            results = service.search_jobs(
                company=company,
                skills=skills_list,
                location=location,
                job_type=job_type,
                limit=limit
            )
            
            progress.remove_task(task)
        
        if not results:
            console.print("No jobs found matching your criteria.", style="yellow")
            return
        
        console.print(f"Found {len(results)} job(s)", style="green")
        
        if output_format == 'table':
            _display_jobs_table(results)
        elif output_format == 'json':
            console.print(json.dumps(results, indent=2, default=str))
        elif output_format == 'summary':
            _display_jobs_summary(results)
            
    except Exception as e:
        console.print(f"❌ Error searching jobs: {e}", style="red")

@cli.command()
@click.argument('job_id')
@click.option('--format', 'output_format', default='detailed',
              type=click.Choice(['detailed', 'json', 'summary']),
              help='Output format')
def show(job_id: str, output_format: str):
    """Show detailed information about a specific job."""
    
    try:
        service = JobDatabaseService()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("📋 Retrieving job details...", total=None)
            job_data = service.get_job_by_id(job_id)
            progress.remove_task(task)
        
        if not job_data:
            console.print(f"❌ Job with ID {job_id} not found", style="red")
            return
        
        if output_format == 'json':
            console.print(json.dumps(job_data, indent=2, default=str))
        elif output_format == 'summary':
            _display_job_summary(job_data)
        else:
            _display_job_detailed(job_data)
            
    except Exception as e:
        console.print(f"❌ Error retrieving job: {e}", style="red")

@cli.command()
@click.argument('job_id')
@click.argument('status', type=click.Choice(['active', 'applied', 'rejected', 'interview', 'offer']))
def update_status(job_id: str, status: str):
    """Update the status of a job."""
    
    try:
        service = JobDatabaseService()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"📝 Updating job status to {status}...", total=None)
            success = service.update_job_status(job_id, status)
            progress.remove_task(task)
        
        if success:
            console.print(f"✅ Job {job_id} status updated to {status}", style="green")
        else:
            console.print(f"❌ Failed to update job status", style="red")
            
    except Exception as e:
        console.print(f"❌ Error updating job status: {e}", style="red")

@cli.command()
def interactive():
    """Interactive job parsing session."""
    
    console.print(Panel.fit(
        "🚀 [bold blue]Interactive Job Parser[/bold blue]\n"
        "Parse job descriptions interactively with guided prompts.",
        border_style="blue"
    ))
    
    while True:
        console.print("\n" + "="*50)
        
        # Get input method
        method = Prompt.ask(
            "How would you like to input the job description?",
            choices=["url", "text", "file", "quit"],
            default="url"
        )
        
        if method == "quit":
            console.print("👋 Goodbye!", style="blue")
            break
        
        try:
            if method == "url":
                url = Prompt.ask("Enter job posting URL")
                service = JobDatabaseService()
                result = service.process_job_from_url(url)
                
            elif method == "text":
                console.print("Enter job description (press Ctrl+D when done):")
                text_lines = []
                try:
                    while True:
                        line = input()
                        text_lines.append(line)
                except EOFError:
                    pass
                
                text = '\n'.join(text_lines)
                service = JobDatabaseService()
                result = service.process_job_from_text(text)
                
            elif method == "file":
                file_path = Prompt.ask("Enter file path")
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                service = JobDatabaseService()
                result = service.process_job_from_text(file_content)
            
            # Display results
            if result["status"] == "success":
                console.print("✅ Job parsed successfully!", style="green bold")
                _display_job_result(result)
                
                if "validation" in result:
                    _display_validation_results(result["validation"])
            else:
                console.print(f"❌ Parsing failed: {result['message']}", style="red")
            
            # Ask if user wants to continue
            if not Confirm.ask("\nWould you like to parse another job?"):
                break
                
        except KeyboardInterrupt:
            console.print("\n👋 Goodbye!", style="blue")
            break
        except Exception as e:
            console.print(f"❌ Error: {e}", style="red")

def _display_job_result(result):
    """Display job processing result."""
    data = result["parsed_data"]
    
    table = Table(title="📋 Parsed Job Information")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="white")
    
    table.add_row("Job ID", str(result.get("job_id", "N/A")))
    table.add_row("Title", data["title"])
    table.add_row("Company", data["company"])
    table.add_row("Location", data["location"])
    table.add_row("Required Skills", str(data["required_skills_count"]))
    table.add_row("Technologies", str(data["technologies_count"]))
    
    console.print(table)

def _display_job_details(job_details):
    """Display detailed job information."""
    
    # Basic info panel
    basic_info = f"""
[bold blue]Title:[/bold blue] {job_details.title}
[bold blue]Company:[/bold blue] {job_details.company}
[bold blue]Location:[/bold blue] {job_details.location}
[bold blue]Type:[/bold blue] {job_details.job_type}
[bold blue]Remote Policy:[/bold blue] {job_details.remote_policy}
"""
    
    console.print(Panel(basic_info, title="📋 Job Information", border_style="blue"))
    
    # Skills table
    if job_details.requirements.required_skills or job_details.requirements.preferred_skills:
        skills_table = Table(title="🛠️ Skills & Requirements")
        skills_table.add_column("Type", style="cyan")
        skills_table.add_column("Skills", style="white")
        
        if job_details.requirements.required_skills:
            skills_table.add_row("Required", ", ".join(job_details.requirements.required_skills))
        if job_details.requirements.preferred_skills:
            skills_table.add_row("Preferred", ", ".join(job_details.requirements.preferred_skills))
        if job_details.requirements.technologies:
            skills_table.add_row("Technologies", ", ".join(job_details.requirements.technologies))
        
        console.print(skills_table)

def _display_jobs_table(jobs):
    """Display jobs in table format."""
    table = Table(title="🔍 Job Search Results")
    table.add_column("ID", style="cyan")
    table.add_column("Title", style="white")
    table.add_column("Company", style="green")
    table.add_column("Location", style="yellow")
    table.add_column("Type", style="magenta")
    table.add_column("Status", style="blue")
    
    for job in jobs:
        table.add_row(
            str(job.get("id", ""))[:8],
            job.get("job_title", ""),
            job.get("companies", {}).get("name", "") if job.get("companies") else "",
            job.get("location", ""),
            job.get("job_type", ""),
            job.get("status", "")
        )
    
    console.print(table)

def _display_jobs_summary(jobs):
    """Display jobs in summary format."""
    for i, job in enumerate(jobs, 1):
        company_name = job.get("companies", {}).get("name", "") if job.get("companies") else ""
        
        summary = f"""
[bold blue]{i}. {job.get('job_title', 'Unknown Title')}[/bold blue]
   Company: {company_name}
   Location: {job.get('location', 'Not specified')}
   Type: {job.get('job_type', 'Not specified')}
   Status: {job.get('status', 'Unknown')}
   ID: {str(job.get('id', ''))[:8]}
"""
        console.print(summary)

def _display_job_detailed(job_data):
    """Display detailed job information."""
    company_name = job_data.get("companies", {}).get("name", "") if job_data.get("companies") else ""
    
    # Basic info
    basic_info = f"""
[bold blue]Title:[/bold blue] {job_data.get('job_title', 'N/A')}
[bold blue]Company:[/bold blue] {company_name}
[bold blue]Location:[/bold blue] {job_data.get('location', 'N/A')}
[bold blue]Type:[/bold blue] {job_data.get('job_type', 'N/A')}
[bold blue]Remote Policy:[/bold blue] {job_data.get('remote_policy', 'N/A')}
[bold blue]Status:[/bold blue] {job_data.get('status', 'N/A')}
"""
    
    console.print(Panel(basic_info, title="📋 Job Information", border_style="blue"))
    
    # Skills and requirements
    skills_data = []
    if job_data.get('required_skills'):
        skills_data.append(("Required Skills", ", ".join(job_data['required_skills'])))
    if job_data.get('preferred_skills'):
        skills_data.append(("Preferred Skills", ", ".join(job_data['preferred_skills'])))
    if job_data.get('technologies'):
        skills_data.append(("Technologies", ", ".join(job_data['technologies'])))
    
    if skills_data:
        skills_table = Table(title="🛠️ Skills & Requirements")
        skills_table.add_column("Type", style="cyan")
        skills_table.add_column("Details", style="white")
        
        for skill_type, skills in skills_data:
            skills_table.add_row(skill_type, skills)
        
        console.print(skills_table)

def _display_job_summary(job_data):
    """Display job summary."""
    company_name = job_data.get("companies", {}).get("name", "") if job_data.get("companies") else ""
    
    summary = f"""
[bold blue]{job_data.get('job_title', 'Unknown Title')}[/bold blue]
Company: {company_name}
Location: {job_data.get('location', 'Not specified')}
Type: {job_data.get('job_type', 'Not specified')}
Status: {job_data.get('status', 'Unknown')}
"""
    console.print(summary)

def _display_validation_results(validation):
    """Display validation results."""
    if validation["missing_required"]:
        console.print(f"⚠️ Missing required fields: {', '.join(validation['missing_required'])}", style="yellow")
    
    if validation["data_quality"]:
        console.print(f"⚠️ Data quality issues: {', '.join(validation['data_quality'])}", style="yellow")
    
    if validation["warnings"]:
        console.print(f"ℹ️ Warnings: {', '.join(validation['warnings'])}", style="blue")

if __name__ == "__main__":
    cli()
