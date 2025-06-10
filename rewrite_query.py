def rewrite_user_query(query):
    replacements = {
        "carry out": "perform",
        "KSAs": "knowledge skills and attitudes",
        "TNA": "training needs analysis",
        "ITP": "individual training plan",
        "TPD": "training performance data",
    }

    for original, replacement in replacements.items():
        query = query.replace(original, replacement)

    return query
