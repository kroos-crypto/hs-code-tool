"""
Umfassender HS Code Classifier fuer Fashion, Kosmetik & Home Goods
Beruecksichtigt: Produktkategorie, Material, Geschlecht, Altersgruppe
"""

def get_primary_material(material):
    m = material.lower()
    if any(t in m for t in ['wool', 'cashmere', 'merino', 'alpaca', 'mohair']):
        return 'wool'
    elif any(t in m for t in ['silk', 'seide']):
        return 'silk'
    elif any(t in m for t in ['cotton', 'baumwolle']):
        return 'cotton'
    elif any(t in m for t in ['linen', 'leinen', 'flax']):
        return 'linen'
    elif any(t in m for t in ['leather', 'leder', 'calf', 'lamb', 'suede', 'nubuck']):
        return 'leather'
    elif any(t in m for t in ['polyester', 'nylon', 'polyamide', 'acrylic',
                               'elastane', 'spandex', 'lycra', 'polypropylene']):
        return 'synthetic'
    elif any(t in m for t in ['viscose', 'modal', 'lyocell', 'tencel', 'rayon', 'acetate', 'cupro']):
        return 'artificial'
    elif any(t in m for t in ['down', 'feather', 'daunen']):
        return 'down'
    return 'cotton'


def classify_hs_code(row):
    category = str(row.get('Boozt Product Category', '')).lower()
    material = str(row.get('Material composition', '')).lower()
    gender = str(row.get('Gender (F = Female, M = Male, U = Unisex)', 'U')).strip().upper()
    name = str(row.get('Style/Display name', '')).lower()
    age_group = str(row.get('Age group', '')).lower()

    mat = get_primary_material(material)
    is_female = gender in ['F', 'U']
    is_kids = any(k in age_group for k in ['kid', 'child', 'baby', 'infant', 'junior', 'girl', 'boy']) \
              or any(k in category for k in ['kids', 'children', 'baby', 'infant', 'junior', 'girl', 'boy'])

    # ===== KOSMETIK / BEAUTY (Kapitel 33) =====
    if any(c in category for c in ['perfume', 'fragrance', 'eau de', 'cologne']):
        return '3303000000'
    if any(c in category for c in ['lip', 'lipstick', 'lip gloss', 'lip balm']):
        return '3304100000'
    if any(c in category for c in ['eye shadow', 'mascara', 'eyeliner', 'eye makeup']):
        return '3304200000'
    if any(c in category for c in ['nail polish', 'nail lacquer', 'manicure', 'pedicure']):
        return '3304300000'
    if any(c in category for c in ['foundation', 'face powder', 'blush', 'bronzer', 'concealer', 'bb cream', 'cc cream']):
        return '3304910000'
    if any(c in category for c in ['skincare', 'moisturiser', 'moisturizer', 'serum', 'face cream',
                                    'body lotion', 'body cream', 'hand cream', 'sunscreen', 'spf',
                                    'cleanser', 'toner', 'makeup', 'cosmetics', 'beauty']):
        return '3304990000'
    if any(c in category for c in ['shampoo', 'conditioner', 'hair mask', 'hair care']):
        return '3305100000'
    if any(c in category for c in ['hair spray', 'hair lacquer', 'dry shampoo']):
        return '3305300000'
    if any(c in category for c in ['hair oil', 'hair serum', 'hair cream', 'hair treatment']):
        return '3305900000'
    if any(c in category for c in ['deodorant', 'antiperspirant']):
        return '3307200000'
    if any(c in category for c in ['soap', 'shower gel', 'body wash', 'bath oil', 'bath salt', 'bath bomb']):
        return '3401110000'

    # ===== HOME GOODS / WOHNTEXTILIEN (Kapitel 63) =====
    if any(c in category for c in ['candle', 'kerze', 'tealight', 'scented candle']):
        return '3406000000'
    if any(c in category for c in ['pillowcase', 'pillow case', 'kissenbezug', 'pillow cover']):
        if mat == 'cotton':
            return '6302210090'
        return '6302220090'
    if any(c in category for c in ['duvet cover', 'bettbezug', 'bettueberw', 'quilt cover', 'bedding set']):
        if mat == 'cotton':
            return '6302210090'
        return '6302220090'
    if any(c in category for c in ['bed linen', 'sheet', 'fitted sheet', 'flat sheet', 'bettwaesche']):
        if mat == 'cotton':
            return '6302210090'
        return '6302220090'
    if any(c in category for c in ['towel', 'handtuch', 'bath towel', 'hand towel', 'face cloth']):
        if mat == 'cotton':
            return '6302600090'
        return '6302600090'
    if any(c in category for c in ['blanket', 'throw', 'decke', 'bedspread', 'bettueberw',
                                    'quilt', 'comforter', 'duvet']):
        if mat in ['wool', 'cashmere']:
            return '6301200090'
        elif mat == 'cotton':
            return '6301400090'
        elif mat == 'down':
            return '9404210090'
        return '6301300090'
    if any(c in category for c in ['cushion', 'pillow', 'kissen']):
        return '9404900090'
    if any(c in category for c in ['curtain', 'vorhang', 'blind', 'drape']):
        if mat == 'cotton':
            return '6303920090'
        return '6303990090'
    if any(c in category for c in ['rug', 'carpet', 'teppich', 'mat']):
        return '5703200090'
    if any(c in category for c in ['vase', 'pot', 'bowl', 'plate', 'mug', 'cup', 'glass', 'home decor', 'decoration']):
        return '6913100000'

    # ===== SCHUHE (Kapitel 64) =====
    shoe_cats = ['shoes', 'boots', 'sneakers', 'sandals', 'mules', 'slides', 'pumps',
                 'loafers', 'clogs', 'heels', 'flats', 'trainers', 'espadrilles',
                 'summer shoes', 'ankle boots', 'knee-high', 'ballerinas', 'ballet flats']
    if any(c in category for c in shoe_cats) or any(c in name for c in ['boot', 'sneaker', 'sandal', 'pump', 'mule', 'loafer']):
        is_leather_shoe = any(t in material for t in ['leather', 'calf', 'lamb', 'suede'])
        is_textile_shoe = any(t in material for t in ['linen', 'polyester', 'nylon', 'canvas', 'textile', 'mesh'])
        covers_ankle = 'boot' in category or 'boot' in name or 'ankle' in name or 'knee' in name
        if is_kids:
            if is_textile_shoe and not is_leather_shoe:
                return '6404112000'
            if covers_ankle:
                return '6403520090'
            return '6403620090'
        if is_textile_shoe and not is_leather_shoe:
            return '6404112000'
        if covers_ankle:
            return '6403992000'
        return '6403911000'

    # ===== KINDER-OBERBEKLEIDUNG (Kapitel 61/62) =====
    if is_kids:
        if any(c in category for c in ['t-shirt', 'top', 'shirt']):
            if mat == 'cotton':
                return '6109100010'
            return '6109900010'
        if any(c in category for c in ['sweater', 'pullover', 'cardigan', 'knitwear', 'jumper']):
            if mat in ['wool', 'cashmere']:
                return '6110110090'
            elif mat == 'cotton':
                return '6110201090'
            return '6110301090'
        if any(c in category for c in ['dress', 'skirt']):
            if mat == 'cotton':
                return '6204420090'
            return '6204430090'
        if any(c in category for c in ['jacket', 'coat', 'outerwear']):
            if mat in ['wool', 'cashmere']:
                return '6202110090'
            elif mat == 'cotton':
                return '6202120090'
            return '6202130090'
        if any(c in category for c in ['trousers', 'pants', 'jeans', 'shorts', 'leggings']):
            if mat == 'cotton':
                return '6204620090'
            return '6204630090'
        # Kinder Fallback
        if mat == 'cotton':
            return '6211420090'
        return '6211430090'

    # ===== T-SHIRTS / TOPS (Kapitel 61 gestrickt) =====
    if any(c in category for c in ['t-shirt', 'tshirt', 'tank top', 'singlet', 'vest top', 'polo']):
        if mat == 'cotton':
            return '6109100010'
        return '6109900010'

    # ===== PULLOVER / STRICKWAREN (Kapitel 61) =====
    if any(c in category for c in ['sweater', 'knitwear', 'jumper', 'pullover', 'cardigan',
                                    'knit', 'turtleneck', 'crewneck']):
        if mat in ['wool', 'cashmere']:
            return '6110110090'
        elif mat == 'cotton':
            return '6110201090'
        return '6110301090'

    # ===== HOODIES / SWEATSHIRTS =====
    if any(c in category for c in ['hoodie', 'sweatshirt', 'fleece']):
        if mat == 'cotton':
            return '6110201090'
        return '6110301090'

    # ===== KLEIDER / DRESSES =====
    if any(c in category for c in ['dress', 'dresses', 'jumpsuit', 'playsuit', 'romper']):
        if mat in ['wool', 'cashmere']:
            return '6204410090'
        elif mat == 'cotton':
            return '6204420090'
        elif mat in ['silk', 'artificial']:
            return '6204490090'
        return '6204430090'

    # ===== ROECKE / SKIRTS =====
    if any(c in category for c in ['skirt', 'skirts', 'mini skirt', 'midi skirt', 'maxi skirt']):
        if mat in ['wool', 'cashmere']:
            return '6204510090'
        elif mat == 'cotton':
            return '6204520090'
        elif mat in ['silk', 'artificial']:
            return '6204590090'
        return '6204530090'

    # ===== BLUSEN / SHIRTS =====
    if any(c in category for c in ['blouse', 'blouses', 'shirt', 'shirts', 'tunic']):
        if is_female:
            if mat == 'silk':
                return '6206100090'
            elif mat in ['wool', 'cashmere']:
                return '6206200090'
            elif mat == 'cotton':
                return '6206300090'
            return '6206400090'
        else:
            if mat == 'cotton':
                return '6205200090'
            return '6205300090'

    # ===== HOSEN / JEANS / TROUSERS =====
    if any(c in category for c in ['trousers', 'pants', 'jeans', 'chinos', 'shorts', 'culottes', 'wide leg']):
        if is_female:
            if mat in ['wool', 'cashmere']:
                return '6204610090'
            elif mat == 'cotton':
                return '6204620090'
            elif mat in ['silk', 'artificial']:
                return '6204690090'
            return '6204630090'
        else:
            if mat in ['wool', 'cashmere']:
                return '6203410090'
            elif mat == 'cotton':
                return '6203420090'
            return '6203430090'

    # ===== LEGGINGS / TIGHTS =====
    if any(c in category for c in ['leggings', 'legging', 'tights', 'stockings', 'hosiery', 'pantyhose']):
        return '6115200090'

    # ===== JACKEN / COATS / OUTERWEAR =====
    if any(c in category for c in ['jacket', 'jackets', 'coat', 'coats', 'outerwear', 'parka',
                                    'anorak', 'windbreaker', 'raincoat', 'puffer', 'down jacket', 'ski jacket']):
        if is_female:
            if mat in ['wool', 'cashmere']:
                return '6202110090'
            elif mat == 'cotton':
                return '6202120090'
            return '6202130090'
        else:
            if mat in ['wool', 'cashmere']:
                return '6201110090'
            elif mat == 'cotton':
                return '6201120090'
            return '6201130090'

    # ===== BLAZER / SAKKOS =====
    if any(c in category for c in ['blazer', 'suit jacket', 'suit']):
        if is_female:
            if mat in ['wool', 'cashmere']:
                return '6204310090'
            elif mat == 'cotton':
                return '6204320090'
            return '6204330090'
        else:
            if mat in ['wool', 'cashmere']:
                return '6203310090'
            elif mat == 'cotton':
                return '6203320090'
            return '6203330090'

    # ===== BADEMODE / SWIMWEAR =====
    if any(c in category for c in ['swimwear', 'bikini', 'swimsuit', 'bathing suit', 'swimming']):
        if is_female:
            return '6112410090'
        return '6112310090'

    # ===== UNTERWAESCHE =====
    if any(c in category for c in ['underwear', 'panties', 'briefs', 'boxer', 'thong', 'knickers', 'lingerie']):
        if is_female:
            if mat == 'cotton':
                return '6108210090'
            return '6108220090'
        else:
            if mat == 'cotton':
                return '6107110090'
            return '6107120090'

    # ===== BH / BRAS =====
    if any(c in category for c in ['bra', 'bras', 'bralette', 'bustier', 'corset']):
        return '6212100090'

    # ===== NACHTWAESCHE =====
    if any(c in category for c in ['pyjama', 'pajama', 'nightwear', 'sleepwear', 'nightdress', 'nightgown', 'robe']):
        if is_female:
            if mat == 'cotton':
                return '6108310090'
            return '6108390090'
        else:
            if mat == 'cotton':
                return '6107210090'
            return '6107290090'

    # ===== SOCKEN =====
    if any(c in category for c in ['socks', 'sock', 'ankle socks', 'knee socks']):
        if mat == 'cotton':
            return '6115950090'
        return '6115960090'

    # ===== SCHALS / SCARVES =====
    if any(c in category for c in ['scarf', 'scarves', 'shawl', 'stole', 'poncho', 'wrap']):
        if mat == 'silk':
            return '6214100090'
        elif mat in ['wool', 'cashmere']:
            return '6214200090'
        elif mat == 'cotton':
            return '6214400090'
        return '6214300090'

    # ===== MUETZEN / HATS =====
    if any(c in category for c in ['hat', 'cap', 'beanie', 'headwear', 'beret', 'bucket hat']):
        return '6505000090'

    # ===== HANDSCHUHE =====
    if any(c in category for c in ['gloves', 'glove', 'mittens']):
        if mat == 'leather':
            return '4203210090'
        return '6116100090'

    # ===== TASCHEN / BAGS =====
    if any(c in category for c in ['bag', 'handbag', 'purse', 'clutch', 'backpack', 'tote',
                                    'shopper', 'crossbody', 'shoulder bag', 'wallet', 'purse']):
        if mat == 'leather':
            return '4202210090'
        return '4202220090'

    # ===== GUERTEL / BELTS =====
    if any(c in category for c in ['belt', 'belts']):
        if mat == 'leather':
            return '4203300000'
        return '6217100090'

    # ===== SONNENBRILLEN =====
    if any(c in category for c in ['sunglasses', 'glasses', 'eyewear']):
        return '9004100000'

    # ===== SCHMUCK =====
    if any(c in category for c in ['jewellery', 'jewelry', 'necklace', 'bracelet', 'earrings', 'ring', 'anklet']):
        return '7117190090'

    # ===== UHREN =====
    if any(c in category for c in ['watch', 'watches']):
        return '9102910000'

    # ===== STANDARD FALLBACK =====
    if is_female:
        if mat == 'cotton':
            return '6211420090'
        return '6211430090'
    else:
        if mat == 'cotton':
            return '6211200090'
        return '6211330090'


def get_notes(code):
    notes = {
        # Kosmetik
        '3303000000': 'Parfuem / Eau de Toilette',
        '3304100000': 'Lippenstift / Lip Makeup',
        '3304200000': 'Augen-Makeup (Mascara, Eyeliner)',
        '3304300000': 'Nagellack / Manikuere-Produkte',
        '3304910000': 'Foundation / Gesichtspuder',
        '3304990000': 'Sonstige Kosmetik / Skincare',
        '3305100000': 'Shampoo / Conditioner',
        '3305300000': 'Haarspray / Haarlack',
        '3305900000': 'Sonstige Haarpflegeprodukte',
        '3307200000': 'Deodorant / Antiperspirant',
        '3401110000': 'Seife / Duschgel / Koerperpflege',
        # Home Goods
        '3406000000': 'Kerzen / Teelichter',
        '6302210090': 'Bettwaesche / Kissenbezug aus Baumwolle',
        '6302220090': 'Bettwaesche / Kissenbezug aus Synthetik',
        '6302600090': 'Handtuecher / Badetuecher',
        '6301200090': 'Decken / Wolldecken',
        '6301300090': 'Decken aus Synthetik',
        '6301400090': 'Decken aus Baumwolle',
        '9404210090': 'Daunendecke / Bettdecke',
        '9404900090': 'Kissen / Dekokissen',
        '6303920090': 'Vorhaenge aus Baumwolle',
        '6303990090': 'Vorhaenge aus Synthetik',
        '5703200090': 'Teppiche / Laeuferteppiche',
        '6913100000': 'Vasen / Dekoration aus Keramik/Porzellan',
        # Schuhe
        '6403911000': 'Damen-Lederschuhe, nicht ueber Knoechel',
        '6403992000': 'Damen-Lederschuhe, ueber Knoechel (Stiefel)',
        '6403520090': 'Kinder-Lederschuhe, Knoechelhoehe',
        '6403620090': 'Kinder-Lederschuhe, flach',
        '6404112000': 'Schuhe mit Textilschaft / Gummisohle',
        # T-Shirts
        '6109100010': 'T-Shirts/Tops aus Baumwolle',
        '6109900010': 'T-Shirts/Tops aus anderen Materialien',
        # Pullover
        '6110110090': 'Pullover/Strickwaren aus Wolle/Kaschmir',
        '6110201090': 'Pullover/Strickwaren aus Baumwolle',
        '6110301090': 'Pullover/Strickwaren aus Synthetik',
        # Kleider
        '6204410090': 'Damen-Kleider aus Wolle',
        '6204420090': 'Damen-Kleider aus Baumwolle',
        '6204430090': 'Damen-Kleider aus Synthetik',
        '6204490090': 'Damen-Kleider aus Seide/Kunstfaser',
        # Roecke
        '6204510090': 'Damen-Roecke aus Wolle',
        '6204520090': 'Damen-Roecke aus Baumwolle',
        '6204530090': 'Damen-Roecke aus Synthetik',
        '6204590090': 'Damen-Roecke aus anderen Materialien',
        # Blusen
        '6206100090': 'Damen-Blusen aus Seide',
        '6206200090': 'Damen-Blusen aus Wolle',
        '6206300090': 'Damen-Blusen aus Baumwolle',
        '6206400090': 'Damen-Blusen aus Synthetik',
        '6205200090': 'Herren-Hemden aus Baumwolle',
        '6205300090': 'Herren-Hemden aus Synthetik',
        # Hosen
        '6204610090': 'Damen-Hosen aus Wolle',
        '6204620090': 'Damen-Hosen/Jeans aus Baumwolle',
        '6204630090': 'Damen-Hosen aus Synthetik',
        '6204690090': 'Damen-Hosen aus anderen Materialien',
        '6203410090': 'Herren-Hosen aus Wolle',
        '6203420090': 'Herren-Hosen/Jeans aus Baumwolle',
        '6203430090': 'Herren-Hosen aus Synthetik',
        # Leggings
        '6115200090': 'Leggings / Strumpfhosen',
        # Jacken
        '6202110090': 'Damen-Maentel/Jacken aus Wolle',
        '6202120090': 'Damen-Maentel/Jacken aus Baumwolle',
        '6202130090': 'Damen-Maentel/Jacken aus Synthetik',
        '6201110090': 'Herren-Maentel/Jacken aus Wolle',
        '6201120090': 'Herren-Maentel/Jacken aus Baumwolle',
        '6201130090': 'Herren-Maentel/Jacken aus Synthetik',
        # Blazer
        '6204310090': 'Damen-Blazer aus Wolle',
        '6204320090': 'Damen-Blazer aus Baumwolle',
        '6204330090': 'Damen-Blazer aus Synthetik',
        '6203310090': 'Herren-Sakko aus Wolle',
        '6203320090': 'Herren-Sakko aus Baumwolle',
        '6203330090': 'Herren-Sakko aus Synthetik',
        # Bademode
        '6112410090': 'Damen-Bademode',
        '6112310090': 'Herren-Bademode',
        # Unterwaesche
        '6108210090': 'Damen-Unterwaesche aus Baumwolle',
        '6108220090': 'Damen-Unterwaesche aus Synthetik',
        '6107110090': 'Herren-Unterwaesche aus Baumwolle',
        '6107120090': 'Herren-Unterwaesche aus Synthetik',
        '6212100090': 'BH / Bustier',
        # Nachtwaesche
        '6108310090': 'Damen-Nachtwaesche aus Baumwolle',
        '6108390090': 'Damen-Nachtwaesche aus anderen Materialien',
        '6107210090': 'Herren-Nachtwaesche aus Baumwolle',
        '6107290090': 'Herren-Nachtwaesche aus anderen Materialien',
        # Socken
        '6115950090': 'Socken aus Baumwolle',
        '6115960090': 'Socken aus Synthetik',
        # Schals
        '6214100090': 'Schals aus Seide',
        '6214200090': 'Schals aus Wolle/Kaschmir',
        '6214300090': 'Schals aus Synthetik',
        '6214400090': 'Schals aus Baumwolle',
        # Accessoires
        '6505000090': 'Muetzen / Huete',
        '4203210090': 'Handschuhe aus Leder',
        '6116100090': 'Handschuhe aus Textil',
        '4202210090': 'Taschen aus Leder',
        '4202220090': 'Taschen aus Textil',
        '4203300000': 'Guertel aus Leder',
        '6217100090': 'Guertel aus Textil',
        '9004100000': 'Sonnenbrillen',
        '7117190090': 'Modeschmuck',
        '9102910000': 'Uhren',
        # Fallback
        '6211420090': 'Sonstige Damen-Oberbekleidung aus Baumwolle/Wolle',
        '6211430090': 'Sonstige Damen-Oberbekleidung aus Synthetik',
        '6211200090': 'Sonstige Herren-Oberbekleidung aus Baumwolle',
        '6211330090': 'Sonstige Herren-Oberbekleidung aus Synthetik',
    }
    return notes.get(code, 'Bitte manuell auf Tulltaxan verifizieren')
