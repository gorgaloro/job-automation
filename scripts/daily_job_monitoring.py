#!/usr/bin/env python3
"""
Daily Job Status Monitoring Script
Automated job posting lifecycle tracking and closure detection

This script should be run daily via cron job to:
1. Check all active job postings for availability
2. Detect closed/expired jobs
3. Update job status and calculate posting duration
4. Generate monitoring reports
5. Send alerts for significant changes

Usage:
    python daily_job_monitoring.py [--dry-run] [--max-jobs=100] [--report-email=user@example.com]
"""

import asyncio
import argparse
import logging
import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.job_data_model import Job
from src.core.job_status_monitor import JobStatusMonitor, run_daily_job_monitoring
from src.integrations.supabase.jobs_service import JobsService  # Assuming this exists

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/job_monitoring.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class JobMonitoringOrchestrator:
    """Orchestrates daily job monitoring workflow"""
    
    def __init__(self, dry_run: bool = False, max_jobs: int = None):
        self.dry_run = dry_run
        self.max_jobs = max_jobs
        self.jobs_service = JobsService()
        
    async def load_active_jobs(self) -> List[Job]:
        """Load active jobs from database"""
        try:
            # Get all active jobs that need verification
            jobs = await self.jobs_service.get_active_jobs(limit=self.max_jobs)
            logger.info(f"Loaded {len(jobs)} active jobs from database")
            return jobs
        except Exception as e:
            logger.error(f"Failed to load jobs from database: {e}")
            return []
    
    async def save_updated_jobs(self, jobs: List[Job]) -> bool:
        """Save updated job statuses to database"""
        if self.dry_run:
            logger.info("DRY RUN: Would save updated job statuses to database")
            return True
        
        try:
            updated_count = 0
            for job in jobs:
                if await self.jobs_service.update_job_status(job):
                    updated_count += 1
            
            logger.info(f"Updated {updated_count} job records in database")
            return True
        except Exception as e:
            logger.error(f"Failed to save updated jobs: {e}")
            return False
    
    async def run_monitoring_cycle(self) -> Dict[str, Any]:
        """Run complete monitoring cycle"""
        logger.info("Starting daily job monitoring cycle")
        
        # Load active jobs
        jobs = await self.load_active_jobs()
        if not jobs:
            logger.warning("No jobs loaded for monitoring")
            return {'error': 'No jobs to monitor'}
        
        # Run monitoring
        updated_jobs, report = await run_daily_job_monitoring(jobs)
        
        # Save results
        if not await self.save_updated_jobs(updated_jobs):
            logger.error("Failed to save monitoring results")
            return {'error': 'Failed to save results'}
        
        # Generate comprehensive report
        monitoring_report = {
            'timestamp': datetime.now().isoformat(),
            'dry_run': self.dry_run,
            'jobs_processed': len(jobs),
            'monitoring_stats': {
                'total_checked': report['summary']['total_jobs'],
                'active_found': report['summary']['active_jobs'],
                'closed_detected': report['summary']['closed_jobs'],
                'verification_errors': report['verification_stats']['total_failures']
            },
            'posting_duration_stats': report['posting_duration_stats'],
            'closure_reasons': report['closure_reasons'],
            'age_distribution': report['age_distribution'],
            'alerts': self._generate_alerts(report)
        }
        
        logger.info(f"Monitoring cycle complete: {monitoring_report['monitoring_stats']}")
        return monitoring_report
    
    def _generate_alerts(self, report: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate alerts based on monitoring results"""
        alerts = []
        
        # Alert if many jobs closed recently
        closed_jobs = report['summary']['closed_jobs']
        if closed_jobs > 10:
            alerts.append({
                'type': 'high_closure_rate',
                'message': f'{closed_jobs} jobs detected as closed in this cycle',
                'severity': 'warning'
            })
        
        # Alert if verification failure rate is high
        failure_rate = (report['verification_stats']['total_failures'] / 
                       max(report['summary']['total_jobs'], 1))
        if failure_rate > 0.2:
            alerts.append({
                'type': 'high_failure_rate',
                'message': f'High verification failure rate: {failure_rate:.1%}',
                'severity': 'error'
            })
        
        # Alert if many old jobs are still active
        old_jobs = report['age_distribution'].get('30+_days', 0)
        if old_jobs > 20:
            alerts.append({
                'type': 'stale_jobs',
                'message': f'{old_jobs} jobs are over 30 days old and still active',
                'severity': 'info'
            })
        
        return alerts
    
    def save_report(self, report: Dict[str, Any], filename: str = None) -> str:
        """Save monitoring report to file"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'/var/log/job_monitoring_report_{timestamp}.json'
        
        try:
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            logger.info(f"Report saved to {filename}")
            return filename
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
            return None
    
    def send_email_report(self, report: Dict[str, Any], email: str) -> bool:
        """Send monitoring report via email"""
        if self.dry_run:
            logger.info(f"DRY RUN: Would send email report to {email}")
            return True
        
        try:
            # Create email content
            subject = f"Job Monitoring Report - {datetime.now().strftime('%Y-%m-%d')}"
            
            # Generate HTML report
            html_content = self._generate_html_report(report)
            
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = os.getenv('SMTP_FROM_EMAIL', 'noreply@jobsearch.com')
            msg['To'] = email
            
            # Add HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            smtp_server = os.getenv('SMTP_SERVER', 'localhost')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            smtp_user = os.getenv('SMTP_USER')
            smtp_pass = os.getenv('SMTP_PASS')
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                if smtp_user and smtp_pass:
                    server.starttls()
                    server.login(smtp_user, smtp_pass)
                server.send_message(msg)
            
            logger.info(f"Email report sent to {email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email report: {e}")
            return False
    
    def _generate_html_report(self, report: Dict[str, Any]) -> str:
        """Generate HTML email report"""
        alerts_html = ""
        if report['alerts']:
            alerts_html = "<h3>🚨 Alerts</h3><ul>"
            for alert in report['alerts']:
                severity_emoji = {'error': '❌', 'warning': '⚠️', 'info': 'ℹ️'}
                alerts_html += f"<li>{severity_emoji.get(alert['severity'], '•')} {alert['message']}</li>"
            alerts_html += "</ul>"
        
        return f"""
        <html>
        <body>
            <h2>📊 Daily Job Monitoring Report</h2>
            <p><strong>Date:</strong> {report['timestamp']}</p>
            
            {alerts_html}
            
            <h3>📈 Summary Statistics</h3>
            <ul>
                <li><strong>Jobs Processed:</strong> {report['jobs_processed']}</li>
                <li><strong>Active Jobs:</strong> {report['monitoring_stats']['active_found']}</li>
                <li><strong>Closed Jobs Detected:</strong> {report['monitoring_stats']['closed_detected']}</li>
                <li><strong>Verification Errors:</strong> {report['monitoring_stats']['verification_errors']}</li>
            </ul>
            
            <h3>⏱️ Posting Duration Stats</h3>
            <ul>
                <li><strong>Average Duration:</strong> {report['posting_duration_stats']['average_days']:.1f} days</li>
                <li><strong>Min Duration:</strong> {report['posting_duration_stats']['min_days']} days</li>
                <li><strong>Max Duration:</strong> {report['posting_duration_stats']['max_days']} days</li>
            </ul>
            
            <h3>📅 Job Age Distribution</h3>
            <ul>
                <li><strong>0-7 days:</strong> {report['age_distribution']['0-7_days']} jobs</li>
                <li><strong>8-14 days:</strong> {report['age_distribution']['8-14_days']} jobs</li>
                <li><strong>15-30 days:</strong> {report['age_distribution']['15-30_days']} jobs</li>
                <li><strong>30+ days:</strong> {report['age_distribution']['30+_days']} jobs</li>
            </ul>
            
            <h3>🔍 Closure Reasons</h3>
            <ul>
        """ + "".join([f"<li><strong>{reason}:</strong> {count} jobs</li>" 
                      for reason, count in report['closure_reasons'].items()]) + """
            </ul>
            
            <p><em>Generated by Job Search Automation Platform</em></p>
        </body>
        </html>
        """


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Daily Job Status Monitoring')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Run in dry-run mode (no database updates)')
    parser.add_argument('--max-jobs', type=int, default=None,
                       help='Maximum number of jobs to process')
    parser.add_argument('--report-email', type=str,
                       help='Email address to send report to')
    parser.add_argument('--save-report', type=str,
                       help='File path to save JSON report')
    
    args = parser.parse_args()
    
    # Initialize orchestrator
    orchestrator = JobMonitoringOrchestrator(
        dry_run=args.dry_run,
        max_jobs=args.max_jobs
    )
    
    try:
        # Run monitoring cycle
        report = await orchestrator.run_monitoring_cycle()
        
        if 'error' in report:
            logger.error(f"Monitoring failed: {report['error']}")
            sys.exit(1)
        
        # Save report if requested
        if args.save_report:
            orchestrator.save_report(report, args.save_report)
        
        # Send email report if requested
        if args.report_email:
            orchestrator.send_email_report(report, args.report_email)
        
        # Print summary
        stats = report['monitoring_stats']
        print(f"\n✅ Monitoring Complete!")
        print(f"   Jobs Processed: {report['jobs_processed']}")
        print(f"   Active: {stats['active_found']}")
        print(f"   Closed: {stats['closed_detected']}")
        print(f"   Errors: {stats['verification_errors']}")
        
        if report['alerts']:
            print(f"\n⚠️  {len(report['alerts'])} alerts generated")
            for alert in report['alerts']:
                print(f"   • {alert['message']}")
        
    except Exception as e:
        logger.error(f"Monitoring script failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
