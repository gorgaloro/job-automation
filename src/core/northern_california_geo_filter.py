"""
Northern California Geographic Filter
Filters and classifies jobs within Northern California regions
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class NorCalRegion(Enum):
    BAY_AREA = "Bay Area"
    SACRAMENTO_VALLEY = "Sacramento Valley"
    CENTRAL_VALLEY = "Central Valley"
    NORTH_COAST = "North Coast"
    SIERRA_NEVADA = "Sierra Nevada"


@dataclass
class GeoClassification:
    """Geographic classification result"""
    is_northern_california: bool
    region: Optional[NorCalRegion] = None
    metro_area: Optional[str] = None
    county: Optional[str] = None
    city: Optional[str] = None
    confidence_score: float = 0.0
    matched_keywords: List[str] = None
    
    def __post_init__(self):
        if self.matched_keywords is None:
            self.matched_keywords = []


class NorthernCaliforniaGeoFilter:
    """Service for filtering and classifying Northern California job locations"""
    
    def __init__(self):
        # Comprehensive Northern California geographic data
        self.regions = {
            NorCalRegion.BAY_AREA: {
                'counties': [
                    'San Francisco', 'San Mateo', 'Santa Clara', 'Alameda', 
                    'Contra Costa', 'Marin', 'Napa', 'Solano', 'Sonoma'
                ],
                'metro_areas': [
                    'San Francisco-Oakland-Berkeley',
                    'San Jose-Sunnyvale-Santa Clara',
                    'Santa Rosa-Petaluma',
                    'Vallejo',
                    'Napa'
                ],
                'cities': [
                    # San Francisco County
                    'San Francisco', 'SF',
                    
                    # San Mateo County
                    'Redwood City', 'San Mateo', 'Palo Alto', 'Menlo Park',
                    'Mountain View', 'Foster City', 'Belmont', 'San Carlos',
                    'Burlingame', 'Millbrae', 'South San Francisco',
                    
                    # Santa Clara County
                    'San Jose', 'Santa Clara', 'Sunnyvale', 'Cupertino',
                    'Los Altos', 'Campbell', 'Saratoga', 'Los Gatos',
                    'Milpitas', 'Fremont', 'Newark', 'Union City',
                    
                    # Alameda County
                    'Oakland', 'Berkeley', 'Fremont', 'Hayward', 'Alameda',
                    'San Leandro', 'Castro Valley', 'Dublin', 'Pleasanton',
                    'Livermore', 'Emeryville', 'Piedmont',
                    
                    # Contra Costa County
                    'Concord', 'Richmond', 'Antioch', 'Pittsburg', 'Walnut Creek',
                    'San Ramon', 'Danville', 'Martinez', 'Brentwood',
                    
                    # Marin County
                    'San Rafael', 'Novato', 'Mill Valley', 'Sausalito',
                    'Tiburon', 'Corte Madera', 'Larkspur',
                    
                    # Napa County
                    'Napa', 'St. Helena', 'Calistoga', 'Yountville',
                    
                    # Solano County
                    'Vallejo', 'Fairfield', 'Vacaville', 'Suisun City',
                    
                    # Sonoma County
                    'Santa Rosa', 'Petaluma', 'Rohnert Park', 'Sebastopol',
                    'Healdsburg', 'Windsor', 'Sonoma'
                ],
                'keywords': [
                    'bay area', 'silicon valley', 'peninsula', 'south bay',
                    'east bay', 'north bay', 'sf bay area', 'san francisco bay'
                ]
            },
            
            NorCalRegion.SACRAMENTO_VALLEY: {
                'counties': [
                    'Sacramento', 'Yolo', 'Placer', 'El Dorado', 'Sutter',
                    'Yuba', 'Colusa', 'Glenn', 'Butte', 'Tehama'
                ],
                'metro_areas': [
                    'Sacramento-Roseville-Folsom',
                    'Chico',
                    'Yuba City'
                ],
                'cities': [
                    # Sacramento County
                    'Sacramento', 'Elk Grove', 'Citrus Heights', 'Folsom',
                    'Rancho Cordova', 'Galt', 'Isleton',
                    
                    # Yolo County
                    'Davis', 'Woodland', 'West Sacramento', 'Winters',
                    
                    # Placer County
                    'Roseville', 'Rocklin', 'Lincoln', 'Auburn', 'Colfax',
                    'Tahoe City', 'Truckee',
                    
                    # El Dorado County
                    'Placerville', 'South Lake Tahoe', 'Cameron Park',
                    
                    # Butte County
                    'Chico', 'Oroville', 'Paradise', 'Gridley',
                    
                    # Other
                    'Yuba City', 'Marysville', 'Colusa', 'Willows'
                ],
                'keywords': [
                    'sacramento valley', 'central valley north', 'greater sacramento'
                ]
            },
            
            NorCalRegion.CENTRAL_VALLEY: {
                'counties': [
                    'San Joaquin', 'Stanislaus', 'Merced', 'Madera',
                    'Fresno', 'Kings', 'Tulare', 'Kern'
                ],
                'metro_areas': [
                    'Stockton',
                    'Modesto',
                    'Merced',
                    'Fresno',
                    'Visalia-Porterville',
                    'Bakersfield'
                ],
                'cities': [
                    # San Joaquin County
                    'Stockton', 'Tracy', 'Manteca', 'Lodi', 'Ripon',
                    
                    # Stanislaus County
                    'Modesto', 'Turlock', 'Ceres', 'Oakdale', 'Patterson',
                    
                    # Merced County
                    'Merced', 'Los Banos', 'Atwater', 'Livingston',
                    
                    # Fresno County
                    'Fresno', 'Clovis', 'Sanger', 'Reedley', 'Selma',
                    
                    # Other Central Valley
                    'Visalia', 'Tulare', 'Porterville', 'Bakersfield',
                    'Delano', 'Madera', 'Hanford', 'Lemoore'
                ],
                'keywords': [
                    'central valley', 'san joaquin valley', 'central california'
                ]
            },
            
            NorCalRegion.NORTH_COAST: {
                'counties': [
                    'Mendocino', 'Lake', 'Humboldt', 'Del Norte'
                ],
                'metro_areas': [
                    'Eureka-Arcata',
                    'Ukiah',
                    'Crescent City'
                ],
                'cities': [
                    'Eureka', 'Arcata', 'Fortuna', 'McKinleyville',
                    'Ukiah', 'Willits', 'Fort Bragg', 'Mendocino',
                    'Clearlake', 'Lakeport', 'Crescent City'
                ],
                'keywords': [
                    'north coast', 'redwood coast', 'humboldt county',
                    'mendocino coast'
                ]
            },
            
            NorCalRegion.SIERRA_NEVADA: {
                'counties': [
                    'Nevada', 'Sierra', 'Plumas', 'Lassen', 'Modoc',
                    'Shasta', 'Siskiyou', 'Alpine', 'Amador', 'Calaveras',
                    'Tuolumne', 'Mariposa', 'Mono', 'Inyo'
                ],
                'metro_areas': [
                    'Redding',
                    'Grass Valley-Nevada City',
                    'Truckee-Tahoe'
                ],
                'cities': [
                    'Redding', 'Anderson', 'Shasta Lake',
                    'Grass Valley', 'Nevada City', 'Auburn',
                    'Truckee', 'South Lake Tahoe', 'Mammoth Lakes',
                    'Bishop', 'Susanville', 'Alturas', 'Yreka',
                    'Jackson', 'Angels Camp', 'Sonora', 'Mariposa'
                ],
                'keywords': [
                    'sierra nevada', 'lake tahoe', 'mountain region',
                    'northern mountains', 'gold country'
                ]
            }
        }
        
        # Alternative names and abbreviations
        self.location_aliases = {
            'sf': 'san francisco',
            'sj': 'san jose',
            'sv': 'silicon valley',
            'peninsula': 'san mateo county',
            'south bay': 'santa clara county',
            'east bay': 'alameda county',
            'north bay': 'marin county',
            'wine country': 'napa county',
            'sac': 'sacramento',
            'the city': 'san francisco',
            'silicon valley': 'santa clara county'
        }
        
        # Remote work indicators that should still be considered if company is in NorCal
        self.remote_indicators = [
            'remote', 'work from home', 'wfh', 'distributed', 'anywhere',
            'remote-first', 'fully remote', 'remote work', 'telecommute'
        ]
    
    def normalize_location(self, location: str) -> str:
        """Normalize location string for matching"""
        if not location:
            return ""
        
        # Convert to lowercase and clean
        normalized = re.sub(r'[^\w\s,-]', ' ', location.lower()).strip()
        
        # Replace common abbreviations
        for alias, full_name in self.location_aliases.items():
            normalized = re.sub(r'\b' + re.escape(alias) + r'\b', full_name, normalized)
        
        # Clean up whitespace
        normalized = re.sub(r'\s+', ' ', normalized)
        
        return normalized
    
    def extract_location_components(self, location: str) -> Dict[str, List[str]]:
        """Extract potential cities, counties, and other location components"""
        if not location:
            return {'cities': [], 'counties': [], 'states': [], 'keywords': []}
        
        normalized = self.normalize_location(location)
        
        # Split by common delimiters
        components = re.split(r'[,;/\-\|]', normalized)
        components = [c.strip() for c in components if c.strip()]
        
        cities = []
        counties = []
        states = []
        keywords = []
        
        for component in components:
            component = component.strip()
            
            # Check for state indicators
            if any(state in component for state in ['california', 'ca', 'calif']):
                states.append(component)
            # Check for county indicators
            elif 'county' in component:
                counties.append(component.replace(' county', ''))
            # Check for area/region keywords
            elif any(keyword in component for keyword in ['area', 'valley', 'bay', 'coast', 'region']):
                keywords.append(component)
            # Assume it's a city
            else:
                cities.append(component)
        
        return {
            'cities': cities,
            'counties': counties,
            'states': states,
            'keywords': keywords
        }
    
    def match_location_to_region(self, location: str) -> Tuple[Optional[NorCalRegion], float, List[str]]:
        """Match location string to Northern California region"""
        if not location:
            return None, 0.0, []
        
        normalized_location = self.normalize_location(location)
        components = self.extract_location_components(location)
        
        best_region = None
        best_score = 0.0
        matched_keywords = []
        
        for region, region_data in self.regions.items():
            score = 0.0
            region_matches = []
            
            # Check counties (highest weight)
            for county in region_data['counties']:
                if county.lower() in normalized_location:
                    score += 1.0
                    region_matches.append(f"county:{county}")
            
            # Check cities (high weight)
            for city in region_data['cities']:
                if city.lower() in normalized_location:
                    score += 0.8
                    region_matches.append(f"city:{city}")
            
            # Check metro areas (medium weight)
            for metro in region_data['metro_areas']:
                if metro.lower() in normalized_location:
                    score += 0.6
                    region_matches.append(f"metro:{metro}")
            
            # Check region keywords (medium weight)
            for keyword in region_data['keywords']:
                if keyword in normalized_location:
                    score += 0.5
                    region_matches.append(f"keyword:{keyword}")
            
            if score > best_score:
                best_score = score
                best_region = region
                matched_keywords = region_matches
        
        return best_region, best_score, matched_keywords
    
    def is_remote_job(self, job_description: str, location: str) -> bool:
        """Check if job is remote work"""
        combined_text = f"{job_description} {location}".lower()
        return any(indicator in combined_text for indicator in self.remote_indicators)
    
    def classify_location(self, location: str, job_description: str = "", 
                         company_location: str = "") -> GeoClassification:
        """Classify job location within Northern California"""
        
        # Check if it's a remote job
        is_remote = self.is_remote_job(job_description, location)
        
        # For remote jobs, check company location if available
        if is_remote and company_location:
            location_to_check = company_location
        else:
            location_to_check = location
        
        # Match to region
        region, score, matches = self.match_location_to_region(location_to_check)
        
        # Extract specific location components
        components = self.extract_location_components(location_to_check)
        
        # Determine specific metro area, county, city
        metro_area = None
        county = None
        city = None
        
        if region:
            region_data = self.regions[region]
            
            # Find most specific matches
            for match in matches:
                match_type, match_value = match.split(':', 1)
                if match_type == 'metro' and not metro_area:
                    metro_area = match_value
                elif match_type == 'county' and not county:
                    county = match_value
                elif match_type == 'city' and not city:
                    city = match_value
        
        # Determine if it's Northern California
        is_norcal = region is not None or score > 0
        
        # Adjust confidence score
        confidence = min(1.0, score)
        if is_remote and company_location:
            confidence *= 0.8  # Slightly lower confidence for remote jobs
        
        return GeoClassification(
            is_northern_california=is_norcal,
            region=region,
            metro_area=metro_area,
            county=county,
            city=city,
            confidence_score=confidence,
            matched_keywords=[m.split(':', 1)[1] for m in matches]
        )
    
    def filter_northern_california_jobs(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter jobs to only include Northern California positions"""
        norcal_jobs = []
        
        for job in jobs:
            location = job.get('location', '')
            description = job.get('description', '')
            company_location = job.get('company_location', '')
            
            geo_classification = self.classify_location(location, description, company_location)
            
            if geo_classification.is_northern_california:
                # Add geo classification to job data
                job['geo_classification'] = {
                    'region': geo_classification.region.value if geo_classification.region else None,
                    'metro_area': geo_classification.metro_area,
                    'county': geo_classification.county,
                    'city': geo_classification.city,
                    'confidence_score': geo_classification.confidence_score,
                    'matched_keywords': geo_classification.matched_keywords
                }
                norcal_jobs.append(job)
        
        return norcal_jobs
    
    def generate_geo_analytics_report(self, geo_classifications: List[GeoClassification]) -> Dict[str, Any]:
        """Generate geographic analytics report"""
        total_jobs = len(geo_classifications)
        norcal_jobs = [g for g in geo_classifications if g.is_northern_california]
        
        # Region distribution
        region_dist = {}
        for geo in norcal_jobs:
            if geo.region:
                region_name = geo.region.value
                region_dist[region_name] = region_dist.get(region_name, 0) + 1
        
        # County distribution
        county_dist = {}
        for geo in norcal_jobs:
            if geo.county:
                county_dist[geo.county] = county_dist.get(geo.county, 0) + 1
        
        # Metro area distribution
        metro_dist = {}
        for geo in norcal_jobs:
            if geo.metro_area:
                metro_dist[geo.metro_area] = metro_dist.get(geo.metro_area, 0) + 1
        
        # City distribution (top 20)
        city_dist = {}
        for geo in norcal_jobs:
            if geo.city:
                city_dist[geo.city] = city_dist.get(geo.city, 0) + 1
        
        # Sort and limit city distribution
        top_cities = dict(sorted(city_dist.items(), key=lambda x: x[1], reverse=True)[:20])
        
        return {
            'summary': {
                'total_jobs_analyzed': total_jobs,
                'northern_california_jobs': len(norcal_jobs),
                'norcal_percentage': len(norcal_jobs) / total_jobs * 100 if total_jobs > 0 else 0,
                'avg_confidence_score': sum(g.confidence_score for g in norcal_jobs) / len(norcal_jobs) if norcal_jobs else 0
            },
            'region_distribution': region_dist,
            'county_distribution': county_dist,
            'metro_area_distribution': metro_dist,
            'top_cities': top_cities,
            'geographic_coverage': {
                'regions_represented': len(region_dist),
                'counties_represented': len(county_dist),
                'metro_areas_represented': len(metro_dist),
                'cities_represented': len(city_dist)
            }
        }


# Utility functions

def filter_jobs_by_region(jobs: List[Dict[str, Any]], target_region: NorCalRegion) -> List[Dict[str, Any]]:
    """Filter jobs by specific Northern California region"""
    geo_filter = NorthernCaliforniaGeoFilter()
    filtered_jobs = []
    
    for job in jobs:
        location = job.get('location', '')
        description = job.get('description', '')
        company_location = job.get('company_location', '')
        
        geo_classification = geo_filter.classify_location(location, description, company_location)
        
        if geo_classification.region == target_region:
            job['geo_classification'] = geo_classification
            filtered_jobs.append(job)
    
    return filtered_jobs


def get_bay_area_jobs_only(jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convenience function to filter only Bay Area jobs"""
    return filter_jobs_by_region(jobs, NorCalRegion.BAY_AREA)
