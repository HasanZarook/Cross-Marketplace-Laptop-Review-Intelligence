"""
Enhanced PDF Specification Extractor for Laptop Specs
Extracts structured data from Lenovo PSREF and HP Datasheet PDFs
"""

import pdfplumber
import re
import json
from pathlib import Path
from typing import Dict, List, Any

class LaptopSpecExtractor:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.brand = self._detect_brand()
        
    def _detect_brand(self) -> str:
        """Detect if PDF is Lenovo or HP"""
        path_lower = self.pdf_path.lower()
        if 'lenovo' in path_lower or 'thinkpad' in path_lower:
            return 'Lenovo'
        elif 'hp' in path_lower or 'probook' in path_lower:
            return 'HP'
        return 'Unknown'
    
    def extract_all(self) -> Dict[str, Any]:
        """Extract all specifications from PDF"""
        with pdfplumber.open(self.pdf_path) as pdf:
            text = '\n'.join(page.extract_text() for page in pdf.pages if page.extract_text())
            
            specs = {
                'source_pdf': Path(self.pdf_path).name,
                'brand': self.brand,
                'model': self._extract_model(text),
                'processor': self._extract_processor(text),
                'memory': self._extract_memory(text),
                'storage': self._extract_storage(text),
                'display': self._extract_display(text),
                'graphics': self._extract_graphics(text),
                'battery': self._extract_battery(text),
                'weight': self._extract_weight(text),
                'dimensions': self._extract_dimensions(text),
                'ports': self._extract_ports(text),
                'wireless': self._extract_wireless(text),
                'operating_system': self._extract_os(text),
                'security': self._extract_security(text),
                'multi_media': self._extract_multimedia(text),
                'monitor': self._extract_monitor(text),
                'chipset': self._extract_chipset(text),
                'colour': self._extract_colour(text),
                'case_material': self._extract_casematerial(text),
                'network': self._extract_network(text),
                'warranty': self._extract_warranty(text),
                'certification': self._extract_certification(text),
                'input_device': self._extract_inputdevice(text),
                'power': self._extract_power(text),
                'raw_text': text[:500]  # First 500 chars for debugging
            }
            
        return specs
    
    def _extract_model(self, text: str) -> str:
        """Extract model name"""
        patterns = [
            r'ThinkPad\s+E14\s+Gen\s+\d+\s*\([^)]+\)',
            r'ProBook\s+\d+\s+G\d+',
            r'ProBook\s+\d+\s+\d+\.?\d*\s+inch\s+G\d+',
            r'Model:\s*([^\n]+)'
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0).strip()
        return "Unknown Model"
    
    def _extract_processor(self, text: str) -> List[str]:
        """Extract processor options"""
        processors = []
        patterns = [
            r'Intel[®]?\s+Core[™]?\s+i[3579]-\d+[A-Z]*',
            r'AMD\s+Ryzen[™]?\s+[3579]\s+\d+[A-Z]*',
            r'Core\s+i[3579]-\d+[A-Z]+',
            r'Processor[s]?:\s*([^\n]+)'
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            processors.extend(matches)
        return list(set(processors)) if processors else ["Not specified"]
    
    def _extract_memory(self, text: str) -> List[str]:
        """Extract RAM options"""
        memory_options = []
        patterns = [
            r'\d+GB\s+(?:soldered\s*\+\s*\d+GB\s+)?DDR[45](?:-\d+)?',
            r'Up to\s+\d+GB.*?DDR[45]',
            r'Memory:\s*([^\n]+)',
            r'RAM:\s*([^\n]+)',
            r'\d+GB\s+DDR[45]'
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            memory_options.extend(matches)
        return list(set(memory_options)) if memory_options else ["Not specified"]
    
    def _extract_storage(self, text: str) -> List[str]:
        """Extract storage options"""
        storage_options = []
        patterns = [
            r'\d+GB\s+(?:PCIe|NVMe|M\.2)?\s*SSD',
            r'\d+TB\s+(?:PCIe|NVMe|M\.2)?\s*SSD',
            r'\d+GB\s+HDD',
            r'\d+TB\s+HDD',
            r'Storage:\s*([^\n]+)',
            r'M\.2\s+\d+\s+SSD',
            r'2\.5["\']?\s+(?:SATA\s+)?(?:HDD|SSD)'
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            storage_options.extend(matches)
        return list(set(storage_options)) if storage_options else ["Not specified"]
    
    def _extract_display(self, text: str) -> Dict[str, Any]:
        """Extract display specifications"""
        display = {}
        
        # Size
        size_match = re.search(r'(\d+\.?\d*)\s*["\']?\s*(?:inch|display)', text, re.IGNORECASE)
        if size_match:
            display['size'] = f"{size_match.group(1)} inches"
        
        # Resolution
        resolution_patterns = [
            r'(\d{3,4})\s*[x×]\s*(\d{3,4})',
            r'FHD|WUXGA|WQXGA|2\.2K|4K|UHD'
        ]
        for pattern in resolution_patterns:
            resolution_match = re.search(pattern, text, re.IGNORECASE)
            if resolution_match:
                if pattern == resolution_patterns[0]:
                    display['resolution'] = f"{resolution_match.group(1)}x{resolution_match.group(2)}"
                else:
                    display['resolution'] = resolution_match.group(0)
                break
        
        # Brightness
        brightness_match = re.search(r'(\d+)\s*nits?', text, re.IGNORECASE)
        if brightness_match:
            display['brightness'] = f"{brightness_match.group(1)} nits"
        
        # Touch
        if re.search(r'touch', text, re.IGNORECASE):
            display['touch'] = 'Yes'
        
        # Anti-glare
        if re.search(r'anti-glare', text, re.IGNORECASE):
            display['anti_glare'] = 'Yes'
        
        return display if display else {"size": "Not specified", "resolution": "Not specified"}
    
    def _extract_graphics(self, text: str) -> List[str]:
        """Extract graphics options"""
        graphics = []
        patterns = [
            r'Intel[®]?\s+(?:Iris[®]?\s+)?(?:Xe\s+)?(?:UHD\s+)?Graphics',
            r'NVIDIA[®]?\s+GeForce\s+[^\n,]+',
            r'AMD\s+Radeon[™]?\s+[^\n,]+',
            r'Graphics:\s*([^\n]+)',
            r'Integrated\s+Graphics'
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            graphics.extend(matches)
        return list(set(graphics)) if graphics else ["Integrated"]
    
    def _extract_battery(self, text: str) -> str:
        """Extract battery information"""
        battery_patterns = [
            r'(\d+)\s*Wh',
            r'Battery:\s*([^\n]+)',
            r'(\d+)-cell'
        ]
        for pattern in battery_patterns:
            battery_match = re.search(pattern, text, re.IGNORECASE)
            if battery_match:
                return battery_match.group(0)
        return "Not specified"
    
    def _extract_weight(self, text: str) -> str:
        """Extract weight"""
        weight_match = re.search(r'(\d+\.?\d*)\s*(?:kg|lbs?|pounds?)', text, re.IGNORECASE)
        if weight_match:
            return weight_match.group(0)
        return "Not specified"
    
    def _extract_dimensions(self, text: str) -> str:
        """Extract dimensions"""
        dim_patterns = [
            r'(\d+\.?\d*)\s*x\s*(\d+\.?\d*)\s*x\s*(\d+\.?\d*)\s*mm',
            r'(\d+\.?\d*)\s*x\s*(\d+\.?\d*)\s*x\s*(\d+\.?\d*)\s*inches?',
            r'Dimensions:\s*([^\n]+)'
        ]
        for pattern in dim_patterns:
            dim_match = re.search(pattern, text, re.IGNORECASE)
            if dim_match:
                return dim_match.group(0)
        return "Not specified"
    
    def _extract_ports(self, text: str) -> List[str]:
        """Extract available ports"""
        ports = []
        port_patterns = [
            r'USB[- ]?C[®]?(?:\s+\d\.\d)?(?:\s+Gen\s+\d)?',
            r'USB[- ]?\d\.\d(?:\s+Gen\s+\d)?',
            r'USB\s+3\.2\s+Gen\s+\d',
            r'HDMI[®]?(?:\s+\d\.?\d?[a-z]?)?',
            r'Thunderbolt[™]?\s+\d',
            r'Ethernet',
            r'RJ-?45',
            r'Audio\s+Jack',
            r'Headphone/Microphone',
            r'SD\s+Card',
            r'DisplayPort[™]?'
        ]
        for pattern in port_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            ports.extend(matches)
        return list(set(ports)) if ports else ["Not specified"]
    
    def _extract_wireless(self, text: str) -> Dict[str, Any]:
        """Extract wireless capabilities"""
        wireless = {
            'wifi_6': bool(re.search(r'Wi-Fi[®]?\s+6(?![E])', text, re.IGNORECASE)),
            'wifi_6e': bool(re.search(r'Wi-Fi[®]?\s+6E', text, re.IGNORECASE)),
            'wifi_5': bool(re.search(r'Wi-Fi[®]?\s+5|802\.11ac', text, re.IGNORECASE)),
            'bluetooth': bool(re.search(r'Bluetooth', text, re.IGNORECASE)),
        }
        
        # Bluetooth version
        bt_version = re.search(r'Bluetooth[®]?\s+(\d+\.?\d*)', text, re.IGNORECASE)
        if bt_version:
            wireless['bluetooth_version'] = bt_version.group(1)
        
        return wireless
    
    def _extract_os(self, text: str) -> List[str]:
        """Extract OS options"""
        os_options = []
        os_patterns = [
            r'Windows\s+11\s+(?:Pro|Home|Enterprise)?',
            r'Windows\s+10\s+(?:Pro|Home|Enterprise)?',
            r'Linux',
            r'Ubuntu',
            r'FreeDOS',
            r'No\s+OS'
        ]
        for pattern in os_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                matches = re.findall(pattern, text, re.IGNORECASE)
                os_options.extend(matches)
        return list(set(os_options)) if os_options else ["Not specified"]
    
    def _extract_security(self, text: str) -> List[str]:
        """Extract security features"""
        security = []
        features = [
            r'TPM\s+\d+\.?\d*',
            r'dTPM\s+\d+\.?\d*',
            r'Fingerprint\s+(?:Reader|Sensor)',
            r'IR\s+Camera',
            r'Privacy\s+Shutter',
            r'Kensington\s+Lock',
            r'Smart\s+Card\s+Reader',
            r'BIOS\s+Password',
            r'Trusted\s+Platform\s+Module'
        ]
        for feature in features:
            matches = re.findall(feature, text, re.IGNORECASE)
            security.extend(matches)
        return list(set(security)) if security else ["Not specified"]
    
    def _extract_multimedia(self, text: str) -> Dict[str, Any]:
        """Extract multimedia features (Camera, Audio, Speakers)"""
        multimedia = {}
        
        # Camera
        camera_patterns = [
            r'(\d+)MP\s+(?:HD\s+)?Camera',
            r'(\d+\.?\d*)MP\s+(?:IR\s+)?(?:HD\s+)?(?:RGB\s+)?Camera',
            r'HD\s+Camera',
            r'FHD\s+Camera',
            r'IR\s+Camera',
            r'Camera:\s*([^\n]+)'
        ]
        for pattern in camera_patterns:
            camera_match = re.search(pattern, text, re.IGNORECASE)
            if camera_match:
                multimedia['camera'] = camera_match.group(0)
                break
        
        # Privacy shutter
        if re.search(r'Privacy\s+Shutter|ThinkShutter|Camera\s+Privacy', text, re.IGNORECASE):
            multimedia['camera_privacy'] = 'Yes'
        
        # Audio/Speakers
        audio_patterns = [
            r'Dual\s+Array\s+Microphone',
            r'Stereo\s+Speakers',
            r'Dolby\s+(?:Audio|Atmos)',
            r'Audio\s+by\s+\w+',
            r'(\d+W)\s+Speakers',
            r'Bang\s+&\s+Olufsen',
            r'DTS\s+Audio'
        ]
        speakers = []
        for pattern in audio_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            speakers.extend(matches)
        if speakers:
            multimedia['audio'] = list(set(speakers))
        
        return multimedia if multimedia else {"camera": "Not specified", "audio": ["Not specified"]}
    
    def _extract_monitor(self, text: str) -> Dict[str, Any]:
        """Extract external monitor support capabilities"""
        monitor = {}
        
        # Number of displays
        display_count = re.search(r'(?:Supports\s+)?up\s+to\s+(\d+)\s+(?:independent\s+)?displays?', text, re.IGNORECASE)
        if display_count:
            monitor['max_displays'] = display_count.group(1)
        
        # Monitor resolutions supported
        resolutions = []
        resolution_patterns = [
            r'(\d{4})x(\d{4})@(\d+)Hz',
            r'(\d{4})x(\d{3,4})@(\d+)Hz',
            r'4K\s+@\s*(\d+)Hz',
            r'5K\s+@\s*(\d+)Hz'
        ]
        for pattern in resolution_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            resolutions.extend([' '.join(m) if isinstance(m, tuple) else m for m in matches])
        if resolutions:
            monitor['supported_resolutions'] = list(set(resolutions))
        
        # Monitor support via different ports
        if re.search(r'HDMI.*?supports.*?(\d{4}x\d{3,4}@\d+Hz)', text, re.IGNORECASE):
            hdmi_res = re.search(r'HDMI.*?supports.*?(\d{4}x\d{3,4}@\d+Hz)', text, re.IGNORECASE)
            monitor['hdmi_support'] = hdmi_res.group(1)
        
        if re.search(r'USB-C.*?supports.*?(\d{4}x\d{3,4}@\d+Hz)', text, re.IGNORECASE):
            usbc_res = re.search(r'USB-C.*?supports.*?(\d{4}x\d{3,4}@\d+Hz)', text, re.IGNORECASE)
            monitor['usbc_support'] = usbc_res.group(1)
        
        if re.search(r'Thunderbolt.*?supports.*?(\d{4}x\d{3,4}@\d+Hz)', text, re.IGNORECASE):
            tb_res = re.search(r'Thunderbolt.*?supports.*?(\d{4}x\d{3,4}@\d+Hz)', text, re.IGNORECASE)
            monitor['thunderbolt_support'] = tb_res.group(1)
        
        return monitor if monitor else {"max_displays": "Not specified"}
    
    def _extract_chipset(self, text: str) -> str:
        """Extract chipset information"""
        chipset_patterns = [
            r'Intel[®]?\s+SoC\s+\(System\s+on\s+Chip\)',
            r'Intel[®]?\s+Chipset',
            r'AMD\s+Chipset',
            r'Chipset:\s*([^\n]+)',
            r'Platform\s+Controller\s+Hub'
        ]
        for pattern in chipset_patterns:
            chipset_match = re.search(pattern, text, re.IGNORECASE)
            if chipset_match:
                return chipset_match.group(0)
        return "Not specified"
    
    def _extract_colour(self, text: str) -> List[str]:
        """Extract available color options"""
        colours = []
        colour_patterns = [
            r'Thunder\s+Black',
            r'Arctic\s+Grey',
            r'Natural\s+Silver',
            r'Pike\s+Silver',
            r'Storm\s+Grey',
            r'Colors?:\s*([^\n]+)',
            r'Colour:\s*([^\n]+)',
            r'\b(?:Black|Silver|Grey|Gray|White|Blue|Red|Gold)\b'
        ]
        for pattern in colour_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            colours.extend(matches)
        return list(set(colours)) if colours else ["Not specified"]
    
    def _extract_casematerial(self, text: str) -> str:
        """Extract case/chassis material"""
        material_patterns = [
            r'Aluminum(?:\s+Chassis)?',
            r'Aluminium(?:\s+Chassis)?',
            r'Magnesium\s+Alloy',
            r'Plastic',
            r'Carbon\s+Fiber',
            r'Metal',
            r'Material:\s*([^\n]+)',
            r'(?:Case|Chassis|Body)\s+Material:\s*([^\n]+)'
        ]
        for pattern in material_patterns:
            material_match = re.search(pattern, text, re.IGNORECASE)
            if material_match:
                return material_match.group(0)
        return "Not specified"
    
    def _extract_network(self, text: str) -> Dict[str, Any]:
        """Extract network/connectivity options"""
        network = {}
        
        # Ethernet
        ethernet_patterns = [
            r'Gigabit\s+Ethernet',
            r'10/100/1000\s+Mbps',
            r'RJ-?45',
            r'Ethernet:\s*([^\n]+)'
        ]
        for pattern in ethernet_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                eth_match = re.search(pattern, text, re.IGNORECASE)
                network['ethernet'] = eth_match.group(0)
                break
        
        # WWAN/LTE/5G
        wwan_patterns = [
            r'WWAN',
            r'LTE',
            r'5G',
            r'4G',
            r'Mobile\s+Broadband',
            r'CAT\d+\s+(?:LTE|4G|5G)'
        ]
        wwan = []
        for pattern in wwan_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                matches = re.findall(pattern, text, re.IGNORECASE)
                wwan.extend(matches)
        if wwan:
            network['wwan'] = list(set(wwan))
        
        # NFC
        if re.search(r'NFC', text, re.IGNORECASE):
            network['nfc'] = 'Yes'
        
        return network if network else {"ethernet": "Not specified"}
    
    def _extract_warranty(self, text: str) -> str:
        """Extract warranty information"""
        warranty_patterns = [
            r'(\d+)[-\s]year\s+(?:limited\s+)?warranty',
            r'(\d+)[-\s]month\s+(?:limited\s+)?warranty',
            r'Warranty:\s*([^\n]+)',
            r'Limited\s+warranty',
            r'(\d+)yr\s+warranty'
        ]
        for pattern in warranty_patterns:
            warranty_match = re.search(pattern, text, re.IGNORECASE)
            if warranty_match:
                return warranty_match.group(0)
        return "Not specified"
    
    def _extract_certification(self, text: str) -> List[str]:
        """Extract certifications and compliance"""
        certifications = []
        cert_patterns = [
            r'ENERGY\s+STAR[®]?',
            r'EPEAT[™]?\s+(?:Gold|Silver|Bronze)?',
            r'TCO\s+Certified',
            r'MIL-STD-810[HG]',
            r'MIL-SPEC',
            r'ISO\s+\d+',
            r'RoHS',
            r'CE',
            r'FCC',
            r'UL',
            r'TÜV',
            r'ErP\s+Lot\s+\d+'
        ]
        for pattern in cert_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            certifications.extend(matches)
        return list(set(certifications)) if certifications else ["Not specified"]
    
    def _extract_inputdevice(self, text: str) -> Dict[str, Any]:
        """Extract input device specifications (Keyboard, Touchpad, Pointing device)"""
        input_device = {}
        
        # Keyboard
        keyboard_patterns = [
            r'Backlit\s+Keyboard',
            r'Spill-resistant\s+Keyboard',
            r'Full-size\s+Keyboard',
            r'(\d+)-key\s+Keyboard',
            r'Numeric\s+Keypad',
            r'TrackPoint',
            r'Keyboard:\s*([^\n]+)'
        ]
        keyboard_features = []
        for pattern in keyboard_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            keyboard_features.extend(matches)
        if keyboard_features:
            input_device['keyboard'] = list(set(keyboard_features))
        
        # Touchpad
        touchpad_patterns = [
            r'Precision\s+Touchpad',
            r'Multi-touch\s+(?:Gesture\s+)?Touchpad',
            r'Touchpad:\s*([^\n]+)',
            r'(\d+\.?\d*)["\']?\s+Touchpad',
            r'Clickpad'
        ]
        for pattern in touchpad_patterns:
            touchpad_match = re.search(pattern, text, re.IGNORECASE)
            if touchpad_match:
                input_device['touchpad'] = touchpad_match.group(0)
                break
        
        # Pointing device
        if re.search(r'TrackPoint', text, re.IGNORECASE):
            input_device['pointing_device'] = 'TrackPoint'
        
        return input_device if input_device else {"keyboard": ["Not specified"], "touchpad": "Not specified"}
    
    def _extract_power(self, text: str) -> Dict[str, Any]:
        """Extract power adapter and power delivery specifications"""
        power = {}
        
        # Power adapter wattage
        adapter_patterns = [
            r'(\d+)W\s+(?:AC\s+)?(?:Power\s+)?Adapter',
            r'AC\s+Adapter:\s*(\d+)W',
            r'Power\s+Supply:\s*(\d+)W'
        ]
        for pattern in adapter_patterns:
            adapter_match = re.search(pattern, text, re.IGNORECASE)
            if adapter_match:
                power['adapter_wattage'] = f"{adapter_match.group(1)}W"
                break
        
        # Power Delivery (PD)
        pd_patterns = [
            r'Power\s+Delivery\s+(\d+\.?\d*)',
            r'PD\s+(\d+\.?\d*)',
            r'USB-C.*?Power\s+Delivery'
        ]
        for pattern in pd_patterns:
            pd_match = re.search(pattern, text, re.IGNORECASE)
            if pd_match:
                if 'Power Delivery' in pd_match.group(0):
                    power['power_delivery'] = pd_match.group(0)
                break
        
        # Rapid charging
        if re.search(r'Rapid\s+Charge|Fast\s+Charge|Quick\s+Charge', text, re.IGNORECASE):
            rapid_charge = re.search(r'(?:Rapid|Fast|Quick)\s+Charge(?:\s+\d+%\s+in\s+\d+\s+(?:min|minutes)?)?', text, re.IGNORECASE)
            power['rapid_charge'] = rapid_charge.group(0) if rapid_charge else 'Yes'
        
        # Power consumption
        consumption_match = re.search(r'(?:TDP|Power\s+Consumption):\s*(\d+)W', text, re.IGNORECASE)
        if consumption_match:
            power['power_consumption'] = f"{consumption_match.group(1)}W"
        
        return power if power else {"adapter_wattage": "Not specified"}


def process_all_pdfs(pdf_directory: str, output_file: str):
    """Process all PDFs in directory and save to JSON"""
    pdf_dir = Path(pdf_directory)
    all_specs = []
    
    for pdf_file in pdf_dir.glob('*.pdf'):
        print(f"Processing: {pdf_file.name}")
        try:
            extractor = LaptopSpecExtractor(str(pdf_file))
            specs = extractor.extract_all()
            all_specs.append(specs)
            print(f"✓ Extracted specs for {specs['model']}")
        except Exception as e:
            print(f"✗ Error processing {pdf_file.name}: {e}")
    
    # Save to JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_specs, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Saved {len(all_specs)} laptop specs to {output_file}")
    return all_specs


if __name__ == "__main__":
    # Process all PDFs from Data folder
    specs = process_all_pdfs('data/pdfs', 'laptop_specs_complete.json')
    
    # Print detailed summary
    print("\n=== EXTRACTION SUMMARY ===")
    for spec in specs:
        print(f"\n{'='*60}")
        print(f"{spec['brand']} - {spec['model']}")
        print(f"{'='*60}")
        print(f"  Processors: {len(spec['processor'])} options")
        print(f"  Memory: {len(spec['memory'])} options")
        print(f"  Storage: {len(spec['storage'])} options")
        print(f"  Display: {spec['display']}")
        print(f"  Graphics: {spec['graphics']}")
        print(f"  Battery: {spec['battery']}")
        print(f"  Weight: {spec['weight']}")
        print(f"  Chipset: {spec['chipset']}")
        print(f"  Multimedia: {spec['multi_media']}")
        print(f"  Monitor Support: {spec['monitor']}")
        print(f"  Colour: {spec['colour']}")
        print(f"  Case Material: {spec['case_material']}")
        print(f"  Network: {spec['network']}")
        print(f"  Warranty: {spec['warranty']}")
        print(f"  Certifications: {spec['certification']}")
        print(f"  Input Devices: {spec['input_device']}")
        print(f"  Power: {spec['power']}")
        print(f"  Security: {len(spec['security'])} features")
        print(f"  Ports: {len(spec['ports'])} types")
        print(f"  Wireless: {spec['wireless']}")
        print(f"  OS: {spec['operating_system']}")