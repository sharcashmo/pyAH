""":mod:atlantis.helper.comparable provides helper classes providing
rich comparison operations."""

class RichComparable():
    """Provide its derived classes with rich comparison operations."""
    
    def __eq__(self, other):
        """Return *True* if both objects are equal, *False* otherwise.
        
        :param other: the object current one is compared to.
        
        :return: *True* if both objects are equal, *False* otherwise.
        
        """
        if self.__dict__ == other.__dict__:
            return True
        else:
            return False
