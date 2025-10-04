from bridgeobjects import CALLS
from .images import CALLS_REMOVE

EXTRA_CALLS = ['P', 'D', 'R']
MAXIMUM_BID_LEVEL = 7


class BiddingBox(object):
    """Handle the bidding box for BfG.

        bb_names is a list of bid names

        bb_names is '' if a blank appears in that position in bb_images
    """
    def __init__(self):
        pass

    def refresh(self, bid_history, add_warnings=False):
        """Return a dict of call images for the current bidding box."""
        bb_names = self._bidding_box(bid_history)
        bb_extra_names = self._bidding_box_extras(bid_history, add_warnings)
        return (bb_names, bb_extra_names)

    def _bidding_box(self, bid_history):
        """Return bid box images as a lists of images and names."""
        bb_names = []
        calls_remove = [call for call in EXTRA_CALLS]
        for call in CALLS_REMOVE:
            calls_remove.append(call)
        calls = [call for call in CALLS if call not in calls_remove]
        for call in calls:
            bb_names.append(call)
        bb_names = self._remove_used_from_bidding_box(bb_names, bid_history)
        return bb_names

    def _remove_used_from_bidding_box(self, bb_names, bid_history):
        """Remove bids up to last used from the bidding box."""
        last_bid_index = -1
        for bid in bid_history[::-1]:
            if bid not in ('P', 'D', 'R'):
                last_bid_index = CALLS.index(bid)
                break
        for index in range(last_bid_index+1):
            bb_names[index] = 'blank'
        return bb_names

    def _bidding_box_extras(self, bid_history, add_warnings):
        """Return P and D and R bid box images and names as lists."""
        bb_names = []
        bb_names.append('P')
        if self._can_show_double(bid_history):
            bb_names.append('D')
        if self._can_show_redouble(bid_history):
            bb_names.append('R')
        if add_warnings:
            bb_names.append('alert')
            bb_names.append('stop')
        return bb_names

    @staticmethod
    def _can_show_double(bid_history):
        """Return True if it is appropriate to show Double."""
        def _all_passes():
            """Return True if all bids are passes."""
            for bid in bid_history:
                if bid != 'P':
                    return False
            return True

        if len(bid_history) == 0:
            return False
        if _all_passes():
            return False
        if (bid_history[-1] != 'P' and
                bid_history[-1] != 'D' and
                bid_history[-1] != 'R'):
            return True
        if (len(bid_history) >= 3 and
                bid_history[-3] not in ('P', 'D', 'R') and
                bid_history[-2] == 'P' and
                bid_history[-1] == 'P'):
            return True
        return False

    @staticmethod
    def _can_show_redouble(bid_history):
        """Return True if it is appropriate to show the Redouble."""
        if (len(bid_history) >= 2 and
                bid_history[-1] == 'D'):
            return True
        elif (len(bid_history) >= 4 and
                bid_history[-3] == 'D' and
                bid_history[-2] == 'P' and
                bid_history[-1] == 'P'):
            return True
        else:
            return False
