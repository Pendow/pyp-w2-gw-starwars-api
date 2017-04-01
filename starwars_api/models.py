from starwars_api.client import SWAPIClient
from starwars_api.exceptions import SWAPIClientError

api_client = SWAPIClient()


class BaseModel(object):

    def __init__(self, json_data):
        """
        Dynamically assign all attributes in `json_data` as instance
        attributes of the Model.
        """
        for key,value in json_data.items():
            setattr(self, key, value)
        

    @classmethod
    def get(cls, resource_id):
        """
        Returns an object of current Model requesting data to SWAPI using
        the api_client.
        """
        #People.get(1) => get_people(self, people_id=None, **params) => '/api/people/1'
        model = getattr(api_client, 'get_{}'.format(cls.RESOURCE_NAME))(resource_id)
        
        return cls(model)

    @classmethod
    def all(cls):
        """
        Returns an iterable QuerySet of current Model. The QuerySet will be
        later in charge of performing requests to SWAPI for each of the
        pages while looping.
        """
        return eval("{}QuerySet()".format(cls.RESOURCE_NAME.title()))


class People(BaseModel):
    """Representing a single person"""
    RESOURCE_NAME = 'people'

    def __init__(self, json_data):
        super(People, self).__init__(json_data)

    def __repr__(self):
        return 'Person: {0}'.format(self.name)


class Films(BaseModel):
    RESOURCE_NAME = 'films'

    def __init__(self, json_data):
        super(Films, self).__init__(json_data)

    def __repr__(self):
        return 'Film: {0}'.format(self.title)


class BaseQuerySet(object):

    def __init__(self):
        #People.all() => BaseQuerySet(cls) = BaseQuerySet(People)
        self.get_page = getattr(api_client, 'get_{}'.format(self.RESOURCE_NAME))
        self.page_num = 1
        self.current_page = self.get_page(page=self.page_num)
        self.current_element = 0
        self.record_count = self.current_page['count']
        
        
    #"http://swapi.co/api/people/?page=2"

    def __iter__(self):
        return self.__class__()

    def __next__(self):
        """
        Must handle requests to next pages in SWAPI when objects in the current
        page were all consumed.
        """
        
        if self.current_element < len(self.current_page['results']):
            model = self.current_page['results'][self.current_element]
            self.current_element += 1
            return self._return_item(model)
        try:
            self.current_element = 0
            self.page_num += 1
            self.current_page = self.get_page(page=self.page_num)
            model = self.current_page['results'][self.current_element]
            self.current_element += 1
            return self._return_item(model)
        except SWAPIClientError:
            raise StopIteration
            

    next = __next__

    def count(self):
        """
        Returns the total count of objects of current model.
        If the counter is not persisted as a QuerySet instance attr,
        a new request is performed to the API in order to get it.
        """
        return self.record_count


class PeopleQuerySet(BaseQuerySet):
    RESOURCE_NAME = 'people'

    def __init__(self):
        super(PeopleQuerySet, self).__init__()

    def __repr__(self):
        return 'PeopleQuerySet: {0} objects'.format(str(len(self.objects)))
        
    def _return_item(self, json_data):
        return People(json_data)


class FilmsQuerySet(BaseQuerySet):
    RESOURCE_NAME = 'films'

    def __init__(self):
        super(FilmsQuerySet, self).__init__()

    def __repr__(self):
        return 'FilmsQuerySet: {0} objects'.format(str(len(self.objects)))
    
    def _return_item(self, json_data):
        return Films(json_data)
