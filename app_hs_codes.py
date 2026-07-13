# hs_code_classifier.py
# Boozt-specific HS Code Classifier
# Based on exact Boozt Product Category names and verified codes from ALL.xlsx

import re


def normalize_category(cat):
    """Strip non-breaking spaces and whitespace, lowercase."""
    if not cat or (hasattr(cat, '__class__') and cat.__class__.__name__ == 'float'):
        return ''
    return str(cat).replace('\xa0', '').strip().lower()


def get_primary_material(material_str):
    """Detect primary material from composition string."""
    if not material_str or str(material_str) == 'nan':
        return 'unknown'
    m = str(material_str).lower()

    # Check for upper/outsole split (e.g. "Upper:100% leather;Outsole:100% rubber")
    upper_material = m
    if 'upper:' in m or 'upper :' in m:
        # Extract upper part only for material classification
        upper_parts = re.split(r'[;,]', m)
        for part in upper_parts:
            if 'upper' in part:
                upper_material = part
                break

    u = upper_material
    if any(x in u for x in ['wool', 'merino', 'mohair', 'cashmere', 'alpaca', 'lamb wool', 'lammwolle']):
        return 'wool'
    if any(x in u for x in ['silk', 'seide']):
        return 'silk'
    if any(x in u for x in ['cotton', 'baumwolle', 'coton']):
        return 'cotton'
    if any(x in u for x in ['linen', 'leinen', 'lin ']):
        return 'linen'
    if any(x in u for x in ['leather', 'leder', 'calf', 'suede', 'nubuck', 'naplack',
                              'lamb leather', 'sheep leather', 'pony', 'patent']):
        return 'leather'
    if any(x in u for x in ['rubber', 'gummi']):
        return 'rubber'
    if any(x in u for x in ['viscose', 'rayon', 'modal', 'lyocell', 'tencel', 'cupro']):
        return 'artificial'
    if any(x in u for x in ['polyester', 'polyamide', 'nylon', 'polyurethane',
                              'elastane', 'lycra', 'spandex', 'acrylic', 'polypropylene']):
        return 'synthetic'
    return 'unknown'


def has_leather_sole(material_str):
    """Check if outsole is leather (vs rubber)."""
    if not material_str or str(material_str) == 'nan':
        return False
    m = str(material_str).lower()
    if 'outsole' in m or 'sole:' in m:
        # Find the outsole part
        parts = re.split(r'[;,]', m)
        for part in parts:
            if 'outsole' in part or 'sole:' in part:
                if any(x in part for x in ['leather', 'calf', 'suede']):
                    return True
                if 'rubber' in part or 'synthetic' in part:
                    return False
    # If no explicit outsole info, check general material
    if any(x in m for x in ['leather', 'calf']):
        return True
    return False


def is_sandal_or_thong(name, material_str):
    """Check if item is a sandal, thong, or slingback (open shoe)."""
    n = str(name).lower() if name and str(name) != 'nan' else ''
    return any(x in n for x in ['sandal', 'thong', 'slingback', 'mule', 'slide', 'clog'])


def is_name_wallet(name):
    """Check if the bag is a flat pocketable wallet (NOT a clutch or wallet-bag)."""
    n = str(name).lower() if name and str(name) != 'nan' else ''
    # Clutches are handbags → 4202210090, NOT wallets
    if 'clutch' in n:
        return False
    # Only classify as wallet if name contains clear wallet indicators
    if 'wallet' not in n:
        return False
    # Must also contain a style qualifier to be a flat pocket wallet
    wallet_qualifiers = ['bifold', 'long', 'section', 'coin', 'card', 'compact', 'slim', 'folded', 'zip']
    return any(q in n for q in wallet_qualifiers)


# =============================================================================
# MAIN CLASSIFIER
# =============================================================================

def classify_hs_code(row):
    """
    Classify a product row into a 10-digit TARIC/HS code.
    Uses Boozt Product Category + Material composition + Gender + Style name.
    """
    cat_raw = row.get('Boozt Product Category', '') or ''
    cat = normalize_category(cat_raw)
    gender = str(row.get('Gender (F = Female, M = Male, U = Unisex)', '') or '').strip().upper()
    material = str(row.get('Material composition', '') or '')
    name = str(row.get('Style/Display name', '') or '')

    primary_mat = get_primary_material(material)
    is_male = gender == 'M'

    # =========================================================================
    # SHOES
    # =========================================================================
    if cat == 'boots':
        return _classify_boots(material, primary_mat, is_male)

    if cat == 'rubberboots' or cat == 'rubber boots':
        return '6402991000'

    if cat == 'summer shoes':
        return _classify_summer_shoes(name, material, primary_mat, is_male)

    if cat == 'heeled shoes':
        if primary_mat == 'rubber':
            return '6402991000'
        # Heeled shoes: almost always women's
        if is_male:
            return '6403999690'
        return '6403599100'

    if cat == 'sneakers':
        return _classify_sneakers(material, primary_mat, is_male)

    if cat == 'sports shoes':
        return _classify_sneakers(material, primary_mat, is_male)

    if cat == 'indoor shoes & slippers':
        if primary_mat == 'leather':
            return '6403401000'
        return '6404209090'

    if cat == 'winter shoes':
        if primary_mat == 'rubber':
            return '6402991000'
        if primary_mat == 'leather':
            if is_male:
                return '6403511190'
            return '6403511100'
        return '6403919100'

    # =========================================================================
    # BAGS
    # =========================================================================
    if cat == 'bags':
        return _classify_bags(name, material, primary_mat)

    # =========================================================================
    # BELT
    # =========================================================================
    if cat == 'belt' or cat == 'belts':
        return '4203300090'

    # =========================================================================
    # KNITWEAR (fine/chunky knitted: pullovers, sweaters, cardigans)
    # =========================================================================
    if cat == 'knitwear':
        return _classify_knitwear(material, primary_mat, is_male)

    # =========================================================================
    # T-SHIRTS (short & long sleeved)
    # Note: Boozt has two slightly different T-shirt categories:
    #   "T-Shirts" (capitalized, no spaces) = short-sleeve → 6109100010
    #   " T-shirts " (with non-breaking spaces) = may include long-sleeve/kids → 6110209900
    # =========================================================================
    if cat == 't-shirts':
        # If raw category has non-breaking spaces (kids/long-sleeve subcategory)
        if '\xa0' in str(cat_raw):
            if is_male:
                return '6110209100'
            return '6110209900'
        if is_male:
            if primary_mat == 'wool':
                return '6110113000'
            if primary_mat in ('cotton', 'unknown'):
                return '6109100010'
            if primary_mat == 'synthetic':
                return '6109900090'
            return '6109100010'
        else:
            if primary_mat == 'cotton' or primary_mat == 'unknown':
                return '6109100010'
            if primary_mat == 'synthetic':
                return '6109900090'
            return '6109100010'

    # =========================================================================
    # SWEATSHIRTS & HOODIES (terry/fleece sweatshirts, NOT fine knitwear)
    # =========================================================================
    if cat == 'sweatshirts & hoodies':
        if is_male:
            # Male: cotton → 6110209100; synthetic → 6110309900
            if primary_mat in ('cotton', 'unknown'):
                return '6110209100'
            if primary_mat == 'synthetic':
                return '6110309900'
            return '6110209100'
        else:
            # Female: cotton → 6110209900; synthetic → 6110309900
            if primary_mat in ('cotton', 'unknown'):
                return '6110209900'
            if primary_mat == 'synthetic':
                return '6110309900'
            return '6110209900'

    # =========================================================================
    # POLO SHIRTS
    # =========================================================================
    if cat == 'polo shirts':
        if is_male:
            if primary_mat == 'cotton' or primary_mat == 'unknown':
                return '6105100000'
            if primary_mat == 'synthetic':
                return '6105200000'
            return '6105100000'
        else:
            if primary_mat == 'cotton' or primary_mat == 'unknown':
                return '6106100090'
            return '6106200090'

    # =========================================================================
    # SHIRTS & BLOUSES
    # =========================================================================
    if cat == 'shirts & blouses':
        if is_male:
            if primary_mat == 'cotton' or primary_mat == 'unknown':
                return '6205200000'
            if primary_mat == 'synthetic':
                return '6205300090'
            if primary_mat == 'silk':
                return '6205900010'
            return '6205200000'
        else:
            # Female blouses/shirts
            if primary_mat == 'silk':
                return '6206100000'
            if primary_mat == 'wool':
                return '6206200090'
            if primary_mat == 'cotton':
                return '6206300090'
            if primary_mat == 'synthetic':
                return '6206400000'
            if primary_mat == 'artificial':
                return '6206900090'
            return '6206400000'

    # =========================================================================
    # DRESSES
    # =========================================================================
    if cat == 'dresses':
        if is_male:
            return '6211390090'
        # Female dresses – code based on dominant fiber
        m_lower = str(material).lower()
        # Pure silk → silk code
        if primary_mat == 'silk' and 'wool' not in m_lower and 'polyester' not in m_lower:
            return '6204490010'
        # Predominantly wool (no polyester/cotton)
        if primary_mat == 'wool' and 'polyester' not in m_lower and 'cotton' not in m_lower:
            return '6204410090'
        # Cotton dominant (≥80% cotton) → cotton code even with small amounts of polyester
        cotton_pct = _extract_percentage(m_lower, 'cotton')
        if cotton_pct >= 80:
            return '6204420090'
        # Pure cotton with no synthetic
        if primary_mat == 'cotton' and 'polyester' not in m_lower and 'polyamide' not in m_lower and 'viscose' not in m_lower:
            return '6204420090'
        # Default: synthetic/mixed → 6204430000
        return '6204430000'

    # =========================================================================
    # SKIRTS & SKORTS
    # =========================================================================
    if cat == 'skirts & skorts':
        if primary_mat == 'wool':
            return '6204510090'
        if primary_mat == 'cotton':
            return '6204520090'
        if primary_mat == 'synthetic':
            return '6204530090'
        return '6204590090'

    # =========================================================================
    # JEANS
    # =========================================================================
    if cat == 'jeans':
        if is_male:
            return '6203423100'  # Men's cotton denim jeans
        else:
            return '6204623100'  # Women's cotton denim jeans

    # =========================================================================
    # BOTTOMS / TROUSERS (not jeans)
    # =========================================================================
    if cat == 'bottoms':
        if is_male:
            if primary_mat == 'wool':
                return '6203410090'
            if primary_mat == 'cotton':
                return '6203420090'
            if primary_mat == 'synthetic':
                return '6203430090'
            return '6203420090'
        else:
            if primary_mat == 'wool':
                return '6204610090'
            if primary_mat == 'cotton':
                return '6204620090'
            if primary_mat == 'synthetic':
                return '6204630090'
            return '6204630090'

    # =========================================================================
    # SHORTS
    # =========================================================================
    if cat == 'shorts':
        if is_male:
            if primary_mat == 'cotton':
                return '6203490090'
            return '6203490090'
        else:
            if primary_mat == 'cotton':
                return '6204690090'
            return '6204690090'

    # =========================================================================
    # SWEATPANTS / JOGGERS
    # =========================================================================
    if cat == 'sweatpants':
        if is_male:
            if primary_mat in ('cotton', 'unknown'):
                return '6103410090'
            if primary_mat == 'synthetic':
                return '6103430000'
            return '6103430000'
        else:
            if primary_mat in ('cotton', 'unknown'):
                return '6104130090'
            if primary_mat == 'synthetic':
                return '6104190090'
            return '6104190090'

    # =========================================================================
    # BODIES & BODYSUITS (kids/babies)
    # =========================================================================
    if cat == 'bodies & bodysuits':
        return '6104192000'

    # =========================================================================
    # JUMPSUITS
    # =========================================================================
    if cat == 'jumpsuits':
        if is_male:
            return '6211320090'
        if primary_mat == 'synthetic':
            return '6211430090'
        return '6211420090'

    # =========================================================================
    # OTHER TOPS
    # =========================================================================
    if cat == 'other tops':
        # Fine knitted tops → check if knitted construction
        n = name.lower()
        if any(x in n for x in ['cardigan', 'sweater', 'pullover', 'knit', 'knitwear']):
            return _classify_knitwear(material, primary_mat, is_male)
        # Non-knitted tops → woven/jersey
        if is_male:
            if primary_mat == 'cotton':
                return '6109100010'
            return '6109909000'
        else:
            if primary_mat in ('artificial', 'synthetic', 'unknown'):
                return '6109909000'
            if primary_mat == 'cotton':
                return '6109100010'
            return '6109909000'

    # =========================================================================
    # OUTERWEAR (jackets, coats)
    # =========================================================================
    if cat == 'outerwear':
        if is_male:
            if primary_mat == 'wool':
                return '6201110090'
            if primary_mat == 'cotton':
                return '6201120090'
            if primary_mat in ('synthetic', 'unknown'):
                return '6201130090'
            return '6201130090'
        else:
            if primary_mat == 'wool':
                return '6202110090'
            if primary_mat == 'cotton':
                return '6202120090'
            if primary_mat in ('synthetic', 'unknown'):
                return '6202130090'
            return '6202130090'

    # =========================================================================
    # RAINWEAR
    # =========================================================================
    if cat == 'rainwear':
        if is_male:
            return '6201200090'
        return '6202200090'

    # =========================================================================
    # SUITS & BLAZERS
    # =========================================================================
    if cat == 'suits & blazers':
        if is_male:
            if primary_mat == 'wool':
                return '6203110000'
            if primary_mat == 'cotton':
                return '6203191090'
            return '6203191090'
        else:
            if primary_mat == 'wool':
                return '6204110000'
            return '6204190090'

    # =========================================================================
    # LEATHER CLOTHES
    # =========================================================================
    if cat == 'leather clothes':
        if is_male:
            return '4203100090'
        return '4203100090'

    # =========================================================================
    # LINGERIE & NIGHTWEAR (female)
    # =========================================================================
    if cat == 'lingerie & nightwear':
        n = name.lower()
        if any(x in n for x in ['bra', 'bh', 'bustier']):
            return '6212100090'
        if any(x in n for x in ['brief', 'panty', 'panties', 'slip', 'thong', 'string']):
            return '6212200090'
        if any(x in n for x in ['night', 'pyjama', 'pajama', 'negligee', 'négligée']):
            if primary_mat == 'cotton':
                return '6208210090'
            return '6208910090'
        if primary_mat == 'cotton':
            return '6208210090'
        return '6208910090'

    # =========================================================================
    # NIGHT & UNDERWEAR (male)
    # =========================================================================
    if cat == 'night & underwear':
        n = name.lower()
        if any(x in n for x in ['brief', 'boxer', 'trunk', 'slip', 'underwear']):
            if primary_mat == 'cotton':
                return '6207110000'
            return '6207190090'
        if primary_mat == 'cotton':
            return '6207210090'
        return '6207910090'

    # =========================================================================
    # ROBES / BATHROBES
    # =========================================================================
    if cat == 'robes':
        if is_male:
            return '6207910090'
        if primary_mat == 'cotton':
            return '6208210090'
        return '6208910090'

    # =========================================================================
    # SWIMWEAR
    # =========================================================================
    if cat == 'swimwear':
        if is_male:
            return '6211110000'
        return '6211120000'

    # =========================================================================
    # SPORTSWEAR
    # =========================================================================
    if cat == 'sportswear' or cat == 'sports wear':
        if is_male:
            return '6211320090'
        if primary_mat == 'synthetic':
            return '6211430090'
        return '6211430090'

    # =========================================================================
    # SOCKS
    # =========================================================================
    if cat == 'socks':
        if primary_mat == 'wool':
            return '6115210090'
        if primary_mat == 'cotton':
            return '6115220090'
        return '6115950090'

    # =========================================================================
    # SCARF
    # =========================================================================
    if cat == 'scarf':
        if primary_mat == 'wool':
            return '6214200090'
        if primary_mat == 'silk':
            return '6214100090'
        if primary_mat == 'cotton':
            return '6214300090'
        if primary_mat == 'synthetic':
            return '6214400090'
        return '6214900090'

    # =========================================================================
    # GLOVES & MITTENS
    # =========================================================================
    if cat == 'gloves & mittens':
        if primary_mat == 'leather':
            return '4203210000'
        if primary_mat == 'wool':
            return '6116910090'
        if primary_mat == 'cotton':
            return '6116920090'
        return '6116930090'

    # =========================================================================
    # CAPS & HATS
    # =========================================================================
    if cat == 'caps & hats':
        if primary_mat == 'wool':
            return '6505001000'
        if primary_mat == 'cotton':
            return '6505009030'
        if primary_mat == 'synthetic':
            return '6505009090'
        # Default: knitted/crocheted hat
        return '6505001000'

    # =========================================================================
    # ACCESSORIES (hair clips, scrunchies, etc.)
    # =========================================================================
    if cat == 'accessories':
        n = name.lower()
        # Hair accessories (combs, clips, headbands)
        if any(x in n for x in ['comb', 'clip', 'hairclip', 'scrunchie', 'headband',
                                   'hair clip', 'hair claw', 'barrette']):
            return '9615110000'
        # Jewellery boxes, key rings, sleeping masks
        if 'key' in n or 'ring' in n:
            return '7117190090'
        # Default for accessories (combs / hair items)
        return '9615110000'

    # =========================================================================
    # JEWELLERY (incl. watches)
    # =========================================================================
    if cat == 'jewellery':
        n = name.lower()
        if any(x in n for x in ['watch', 'uhr', 'montre']):
            return '9102110000'
        if 'bracelet' in n:
            return '7117190090'
        if 'necklace' in n or 'chain' in n:
            return '7117190090'
        if 'earring' in n or 'eardob' in n:
            return '7117190090'
        if 'ring' in n:
            return '7117190090'
        return '7117190090'

    # =========================================================================
    # SUNGLASSES
    # =========================================================================
    if cat == 'sunglasses':
        return '9004100000'

    # =========================================================================
    # FOOTWEAR ACCESSORIES
    # =========================================================================
    if cat == 'footwear accessories':
        return '6406200090'

    # =========================================================================
    # DEFAULT FALLBACK
    # =========================================================================
    # If category not recognized, use a generic textile code
    if is_male:
        return '6211320090'
    return '6211430090'


# =============================================================================
# SHOE HELPERS
# =============================================================================

def _classify_boots(material, primary_mat, is_male=False):
    """Classify boots category. Gender affects TARIC code."""
    m = material.lower() if material and str(material) != 'nan' else ''
    # Rubber boots
    if primary_mat == 'rubber':
        return '6402991000'
    # Mixed leather + rubber sole
    if 'rubber' in m and any(x in m for x in ['leather', 'calf', 'suede']):
        if is_male:
            return '6403911110'  # Men's leather boots, rubber sole
        return '6403911190'      # Women's leather boots, rubber sole
    # Leather upper + leather sole → ankle boots
    if primary_mat == 'leather':
        if has_leather_sole(material):
            if is_male:
                return '6403511190'  # Men's leather ankle boots, leather sole
            return '6403511100'      # Women's leather ankle boots, leather sole
        # Leather upper + rubber sole
        if is_male:
            return '6403911110'
        return '6403511190'
    # Synthetic/textile upper
    if primary_mat == 'synthetic':
        return '6402991000'
    # Default
    if is_male:
        return '6403511190'
    return '6403511100'


def _classify_summer_shoes(name, material, primary_mat, is_male=False):
    """Classify summer shoes: ballerinas, sandals, flats, heeled sandals."""
    n = name.lower() if name and str(name) != 'nan' else ''
    m = material.lower() if material and str(material) != 'nan' else ''

    # Textile/synthetic upper
    if primary_mat in ('synthetic', 'cotton', 'linen'):
        if any(x in n for x in ['sandal', 'wedge', 'platform']):
            return '6404209000'
        return '6404209090'

    # Rubber upper
    if primary_mat == 'rubber':
        return '6402200000'

    # Leather upper
    if primary_mat == 'leather':
        leather_sole = has_leather_sole(material)
        is_sandal = is_sandal_or_thong(name, material)

        if is_sandal:
            if leather_sole:
                return '6403200000'   # Sandals, leather upper + leather sole
            else:
                if is_male:
                    return '6403999650'  # Men's sandals, leather upper + rubber sole
                return '6403999190'     # Women's sandals, leather upper + rubber sole
        else:
            # Ballerinas, flats, loafers, pumps (not sandals)
            if is_male:
                return '6403599900'   # Men's leather flat shoes
            return '6403599100'       # Women's leather flat shoes

    # Unknown material → assume leather
    is_sandal = is_sandal_or_thong(name, material)
    if is_sandal:
        return '6403200000'
    if is_male:
        return '6403599900'
    return '6403599100'


def _classify_sneakers(material, primary_mat, is_male=False):
    """Classify sneakers / sports shoes. Gender matters for TARIC code."""
    m = material.lower() if material and str(material) != 'nan' else ''

    # If ANY leather is present → leather sneaker code (leather takes priority)
    if any(x in m for x in ['leather', 'calf', 'suede', 'nubuck', 'naplack']):
        if is_male:
            return '6403999690'  # Men's leather sneakers
        return '6403999890'      # Women's leather sneakers

    # Textile/synthetic upper only → 6404
    if 'upper' in m:
        upper_part = m.split('upper')[1][:80]
        if any(x in upper_part for x in ['cotton', 'polyamide', 'polyester',
                                           'nylon', 'canvas', 'mesh']):
            if is_male:
                return '6404119000'
            return '6404199000'

    if primary_mat in ('cotton', 'synthetic', 'artificial', 'linen'):
        if is_male:
            return '6404119000'
        return '6404199000'

    # Unknown → leather sneaker (luxury/fashion brands)
    if is_male:
        return '6403999690'
    return '6403999890'


def _classify_bags(name, material, primary_mat):
    """Classify bags including wallets."""
    n = name.lower() if name and str(name) != 'nan' else ''

    # Wallets → 4202310090
    if is_name_wallet(n):
        return '4202310090'

    # Leather bags → 4202210090
    if primary_mat == 'leather':
        return '4202210090'
    if any(x in str(material).lower() for x in ['leather', 'calf', 'suede', 'nubuck', 'pony']):
        return '4202210090'
    # Mixed leather/synthetic (still mostly leather) → 4202210090
    m = str(material).lower()
    if 'leather' in m:
        return '4202210090'

    # PU / polyurethane bags
    if 'polyurethane' in m or (' pu ' in m) or m.startswith('pu,') or m.startswith('pu '):
        return '4202221000'

    # Textile bags (cotton, linen, canvas)
    if any(x in m for x in ['cotton', 'linen', 'canvas', 'jute']):
        return '4202229090'

    # Synthetic textile bags
    if any(x in m for x in ['polyester', 'polyamide', 'nylon']):
        return '4202229090'

    # Default: assume leather (most Boozt bags are leather)
    return '4202210090'


def _classify_knitwear(material, primary_mat, is_male):
    """Classify knitwear: pullovers, sweaters, cardigans."""
    m = str(material).lower() if material and str(material) != 'nan' else ''

    # If both wool and cotton present → compare percentages to decide
    if 'wool' in m and 'cotton' in m:
        wool_pct = _extract_percentage(m, 'wool')
        cotton_pct = _extract_percentage(m, 'cotton')
        if cotton_pct >= wool_pct:
            if is_male:
                return '6110209100'
            return '6110209900'
        else:
            # wool dominant
            if is_male:
                if 'mohair' in m:
                    return '6110113000'
                return '6110119000'
            return '6110119000'

    # Pure wool (incl. mohair, merino, cashmere)
    if primary_mat == 'wool':
        if is_male:
            if 'mohair' in m:
                return '6110113000'
            return '6110111000'
        return '6110119000'

    # Cotton knitwear
    if primary_mat == 'cotton':
        if is_male:
            return '6110209100'
        return '6110209900'

    # Synthetic (polyester, polyamide, acrylic)
    if primary_mat == 'synthetic':
        if is_male:
            return '6110309100'
        return '6110309900'

    # Artificial fibers (viscose, modal, etc.)
    if primary_mat == 'artificial':
        if is_male:
            return '6110309100'
        return '6110309900'

    # Default: cotton knitwear
    if is_male:
        return '6110209100'
    return '6110209900'


def _extract_percentage(material_str, fiber):
    """Extract percentage of a fiber from material string."""
    m = material_str.lower()
    pattern = r'(\d+)%\s*' + fiber
    matches = re.findall(pattern, m)
    if matches:
        return int(matches[0])
    return 0


# =============================================================================
# GET NOTES / DESCRIPTIONS
# =============================================================================

HS_CODE_DESCRIPTIONS = {
    # Footwear
    '6402200000': 'Footwear with outer soles and uppers of rubber/plastics, sandals',
    '6402991000': 'Other footwear with rubber/plastic, not covering ankle',
    '6403200000': 'Footwear with leather upper and leather sole, with strap/thong',
    '6403401000': 'Other footwear, leather upper, incorporating protective toe-cap',
    '6403511100': 'Footwear with leather upper, covering ankle, leather sole, women\'s',
    '6403511190': 'Footwear with leather upper, covering ankle, leather sole, other',
    '6403599100': 'Footwear with leather upper, not covering ankle, leather sole, women\'s',
    '6403911190': 'Footwear, leather upper, not covering ankle, rubber sole, other',
    '6403919100': 'Footwear, leather upper, covering ankle, rubber sole',
    '6403999190': 'Other footwear, leather upper, not covering ankle, rubber sole, women\'s',
    '6403999890': 'Other footwear, leather upper, not covering ankle, rubber sole',
    '6404199000': 'Footwear with textile upper, rubber/plastic sole, other',
    '6404209000': 'Footwear with textile upper, leather sole',
    '6404209090': 'Footwear with textile upper, leather/composition leather sole, other',
    '6406200090': 'Footwear accessories',
    # Bags
    '4202210090': 'Handbags and shoulder bags with outer surface of leather',
    '4202221000': 'Handbags with outer surface of plastic sheeting',
    '4202229090': 'Handbags with outer surface of textile materials, other',
    '4202310090': 'Articles carried in pocket/handbag with outer surface of leather (wallets)',
    # Belts
    '4203300090': 'Belts and bandoliers of leather',
    # Knitwear
    '6105100000': 'Men\'s or boys\' shirts, knitted, of cotton',
    '6105200000': 'Men\'s or boys\' shirts, knitted, of artificial/synthetic fibres',
    '6106100090': 'Women\'s or girls\' blouses/shirts, knitted, of cotton',
    '6106200090': 'Women\'s or girls\' blouses/shirts, knitted, of artificial/synthetic',
    '6109100010': 'T-shirts of cotton',
    '6109900090': 'T-shirts and tank tops of other textile materials',
    '6109909000': 'T-shirts/singlets/other vests, of other textile materials',
    '6110111000': 'Jerseys/pullovers, 100% wool, men\'s',
    '6110113000': 'Jerseys/pullovers, wool with mohair, men\'s',
    '6110119000': 'Jerseys/pullovers, wool/fine animal hair, women\'s',
    '6110209100': 'Jerseys/pullovers of cotton, men\'s',
    '6110209900': 'Jerseys/pullovers of cotton, women\'s/other',
    '6110309100': 'Jerseys/pullovers of synthetic fibres, men\'s',
    '6110309900': 'Jerseys/pullovers of synthetic/artificial fibres, women\'s',
    # Trousers / Dresses
    '6103410090': 'Men\'s trousers, bib overalls, of wool or fine animal hair, knitted',
    '6103430000': 'Men\'s trousers, bib overalls, of synthetic fibres, knitted',
    '6104130090': 'Women\'s trousers, bib overalls, knitted, of synthetic fibres',
    '6104192000': 'Girls\' babies\' bodies/bodysuits, knitted, of cotton',
    '6104190090': 'Women\'s knitted trousers/bib overalls, of other textile materials',
    '6201100090': 'Men\'s overcoats of wool or fine animal hair',
    '6201120090': 'Men\'s overcoats of cotton',
    '6201130090': 'Men\'s overcoats of synthetic fibres',
    '6202110090': 'Women\'s overcoats of wool or fine animal hair',
    '6202120090': 'Women\'s overcoats of cotton',
    '6202130090': 'Women\'s overcoats of synthetic fibres',
    '6203110000': 'Men\'s suits of wool or fine animal hair',
    '6203191090': 'Men\'s suits of other textile materials',
    '6203420090': 'Men\'s trousers of cotton',
    '6203423100': 'Men\'s denim trousers of cotton',
    '6203430090': 'Men\'s trousers of synthetic fibres',
    '6203490090': 'Men\'s shorts of other textile materials',
    '6204110000': 'Women\'s suits of wool or fine animal hair',
    '6204190090': 'Women\'s suits of other textile materials',
    '6204410090': 'Women\'s dresses of wool or fine animal hair',
    '6204420090': 'Women\'s dresses of cotton',
    '6204430000': 'Women\'s dresses of synthetic fibres',
    '6204440090': 'Women\'s dresses of artificial fibres',
    '6204490010': 'Women\'s dresses of silk',
    '6204510090': 'Women\'s skirts of wool',
    '6204520090': 'Women\'s skirts of cotton',
    '6204530090': 'Women\'s skirts of synthetic fibres',
    '6204590090': 'Women\'s skirts of other textile materials',
    '6204610090': 'Women\'s trousers of wool',
    '6204620090': 'Women\'s trousers of cotton',
    '6204623100': 'Women\'s denim trousers of cotton',
    '6204630090': 'Women\'s trousers of synthetic fibres',
    '6204690090': 'Women\'s shorts',
    '6205200000': 'Men\'s shirts of cotton',
    '6205300090': 'Men\'s shirts of artificial/synthetic fibres',
    '6205900010': 'Men\'s shirts of silk',
    '6206100000': 'Women\'s blouses/shirts of silk',
    '6206200090': 'Women\'s blouses/shirts of wool',
    '6206300090': 'Women\'s blouses/shirts of cotton',
    '6206400000': 'Women\'s blouses/shirts of artificial/synthetic fibres',
    '6206900090': 'Women\'s blouses/shirts of other textile materials',
    '6207110000': 'Men\'s underpants/briefs of cotton',
    '6207190090': 'Men\'s underpants/briefs of other material',
    '6207210090': 'Men\'s nightshirts/pyjamas of cotton',
    '6207910090': 'Men\'s bathrobes/dressing gowns',
    '6208210090': 'Women\'s nightdresses/pyjamas of cotton',
    '6208910090': 'Women\'s nightdresses/pyjamas of other materials',
    '6211110000': 'Men\'s swimwear',
    '6211120000': 'Women\'s swimwear',
    '6211320090': 'Men\'s garments of cotton (tracksuits/sportswear)',
    '6211430090': 'Women\'s garments of synthetic fibres (sportswear)',
    '6211420090': 'Women\'s garments of cotton',
    '6212100090': 'Brassieres',
    '6212200090': 'Girdles and panty-girdles',
    '6214100090': 'Shawls/scarves of silk',
    '6214200090': 'Shawls/scarves of wool or fine animal hair',
    '6214300090': 'Shawls/scarves of synthetic fibres',
    '6214400090': 'Shawls/scarves of artificial fibres',
    '6214900090': 'Shawls/scarves of other materials',
    '6116100090': 'Impregnated/coated gloves',
    '6116910090': 'Other gloves of wool',
    '6116920090': 'Other gloves of cotton',
    '6116930090': 'Other gloves of synthetic fibres',
    '6115210090': 'Hosiery of wool/fine animal hair',
    '6115220090': 'Hosiery of cotton',
    '6115950090': 'Other hosiery/socks',
    '6505001000': 'Hats and headgear, knitted, of wool',
    '6505009030': 'Hats and headgear, of cotton',
    '6505009090': 'Hats and headgear of other materials',
    '4203100090': 'Leather clothing articles',
    '4203210000': 'Leather protective gloves',
    # Accessories
    '7117190090': 'Imitation jewellery, other',
    '9004100000': 'Sunglasses',
    '9102110000': 'Wrist-watches with automatic winding',
    '9615110000': 'Combs, hair-slides and the like, of hard rubber or plastics',
    '6406200090': 'Outer soles and heels of rubber or plastics',
}


def get_notes(code):
    """Return a human-readable description for an HS code."""
    code_str = str(code).replace(' ', '')
    return HS_CODE_DESCRIPTIONS.get(code_str, f'HS Code {code_str}')
