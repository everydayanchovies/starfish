import functools

from django.conf import settings
from django.db.models import Q

from search import utils
from search.models import Item, Tag, Person

SEARCH_SETTINGS = settings.SEARCH_SETTINGS


def retrieve(query, dict_format=False, communities_list=None):
    '''
    A query contains one or more tokens starting with the following symbols
    @ - indicates user
    # - indicates tags
    " - indicates literal

    These special specials are specified in the SEARCH_SETTINGS setting

    Any query is a conjunction of disjunctions of similar tokens:
    (#tag1 v #tag2 v #tag3) ^ (@user1 v @user2) ^ "literal"
    '''

    # Parse query into tag, person and literal tokens
    tag_tokens, person_tokens, literal_tokens = utils.parse_query(query)

    # Try to find query suggestions
    dym_query, dym_query_raw = utils.did_you_mean(
        tag_tokens, person_tokens, literal_tokens, query, "<b>%s</b>")

    # Extract the tokens, discard location information
    tag_tokens = map(lambda x: x[0], tag_tokens)
    person_tokens = map(lambda x: x[0], person_tokens)
    literal_tokens = map(lambda x: x[0], literal_tokens)

    # Turn token lists in sets to remove duplicates
    tag_tokens = set(tag_tokens)
    person_tokens = set(person_tokens)
    literal_tokens = set(literal_tokens)

    # If literals were used
    if len(literal_tokens) > 0:
        # Store literals in a set
        literals = set([])
        # Lower all literals, and add them to the set
        for literal in literal_tokens:
            literals.add(literal.lower())
        # Convert the set back to a list
        literals = list(literals)
    else:
        # Else, set literals to be empty
        literals = []

    # If tags were used
    if len(tag_tokens) > 0:
        # Fetch all mentioned tags and their aliases
        tags = Tag.objects.select_related('alias_of').filter(
            handle__iregex=r'^(' + '|'.join(tag_tokens) + ')$')
        # Add tag aliases
        tags_extended = set([])
        for tag in tags:
            tags_extended.add(tag)
            if tag.alias_of is not None:
                tags_extended.add(tag.alias_of)
                # Find other aliases that link to the same root tag
                for alias in Tag.objects.filter(alias_of=tag.alias_of):
                    if alias is not tag:
                        tags_extended.add(alias)
            else:
                # If this tag is not an alias,
                # check if other tags are an alias of this tag.
                for alias in Tag.objects.filter(alias_of=tag):
                    tags_extended.add(alias)
        # Use the extended set as list of tags
        tags = list(tags_extended)
    else:
        # Else, set tags to be empty
        tags = []

    # If persons were used
    if len(person_tokens) > 0:
        # If settings set to allow partial person handles
        if SEARCH_SETTINGS['allowPartialPersonHandles']:
            persons = Person.objects.filter(
                handle__iregex=r'^(' + '|'.join(person_tokens) + ')')
        else:
            persons = Person.objects.filter(
                handle__iregex=r'^(' + '|'.join(person_tokens) + ')$')
    else:
        # Else, set persons to be empty
        persons = []

    # If no useful elements could be found in the query
    if len(persons) + len(literals) + len(tags) == 0:
        # Return an empty result
        return query, dym_query, dym_query_raw, [], None

    items = Item.objects.filter(draft=False).select_related()
    # Remove items that are not intended for the current user
    if not communities_list:
        communities_list = []
    else:
        communities_list = functools.reduce(lambda x, y: x + y,
                                            map(lambda c: c.get_parents() + [c], communities_list))
    community_q = functools.reduce(lambda q, c: q | Q(communities=c), communities_list, Q())
    items = items.filter(community_q)

    # Add literal contraints
    if len(literals) > 0:
        # For each literal add a constraint
        for literal in literals:
            items = items.filter(searchablecontent__contains=literal)

    # Add tag constraints
    tags_by_type = {}
    for tag in tags:
        key = tag.type
        if key in tags_by_type:
            tags_by_type[key].append(tag)
        else:
            tags_by_type[key] = [tag]

    if len(tags) > 0:
        for tags in tags_by_type.values():
            items = items.filter(tags__in=tags)

    # Add person constraints
    if len(persons) > 0:
        items = items.filter(links__in=persons)

    # Retrieve the elements
    items = list(items)

    # If settings set to always include mentioned persons
    if SEARCH_SETTINGS['alwaysIncludeMentionedPersons']:
        # If persons were used in filter
        if len(persons) > 0:
            # Add them to the items as well
            for person in persons:
                items.append(person)

    # Ensure items contain no duplicates
    items = list(set(items))

    # Special results that match on specific queries. I.e. a single person or a
    # single tag shows a more detailed view at the top of the results
    special = None
    if len(person_tokens) + len(tag_tokens) + len(literal_tokens) == 1:
        if len(person_tokens) == 1:
            special = persons[0]
        elif len(tag_tokens) == 1:
            # Search through list of extended tags for glossary reference
            for tag in tags:
                if tag.glossary:
                    special = tag.glossary
                    break

    # Remove precise 'special' matches from normal results so that they don't
    # appear twice
    if special:
        items = filter(lambda i: i.id != special.id, items)

    # Initialize results
    results = {}

    # Generate search results
    if dict_format:
        # Ensure unique results
        for item in items:
            # Append the dict_format representation of the item to the results
            results[item.id] = item.dict_format()
        results = results.values()
    else:
        results = items

    # Return the original query, a suggested query and the results
    return query, dym_query, dym_query_raw, results, special


def get_synonyms(tags):
    """Return a set of handles of synonymous tags."""
    all_tags = set()
    for tag in tags:
        try:
            tag_obj = Tag.objects.get(handle__iexact=tag)
        except Tag.DoesNotExist:
            continue

        # Also include original tags
        all_tags.add(tag_obj.handle)

        if tag_obj.alias_of:
            all_tags.add(tag_obj.alias_of.handle)

        synonyms = Tag.objects.filter(alias_of=tag_obj)
        all_tags |= set((s.handle for s in synonyms))
    return all_tags
