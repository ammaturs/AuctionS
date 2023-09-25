from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django import forms
from django.contrib.auth.decorators import login_required
from datetime import datetime

from .models import User, AuctionListing, Watchlist, Comments

CATEGORIES= [
    ("", "Choose a Category"),
    ("electronics", "Electronics"),
    ("clothing", "Clothing"),
    ("collectibles","Collectibles"),
    ("home","Home & Garden"),
    ("toys","Toys & Hobbies"),
    ("jewelry","Jewelry & Watches"),
    ("sporting","Sporting Goods"),
    ("other", "Other")
    ]

#title, description, starting bid, optional url image
class NewCreateForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Name', 'style': 'width: 300px;', 'class': 'form-control'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Description', 'style': 'width: 500px; height:200px;', 'class': 'form-control'}))
    starting_bid = forms.IntegerField(label='Starting bid:',widget=forms.NumberInput(attrs={'placeholder': 'Bid', 'style': 'width: 100px;', 'class': 'form-control'}), min_value=0)
    category = forms.ChoiceField(label='Category:', choices=CATEGORIES)
    image = forms.URLField(label = "Image URL:", required=False)
    created=datetime.now()

class NewCommentForm(forms.Form):
    comment = forms.CharField(label='comment', widget=forms.Textarea(attrs={'placeholder': 'Leave comment here', 'style': 'width: 500px; height:200px;', 'class': 'form-control'}))

def index(request):
    return render(request, "auctions/index.html", {"listings":AuctionListing.objects.all().order_by('created')})

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def create(request):
    if request.method=="POST":
        form=NewCreateForm(request.POST, request.FILES)

        if form.is_valid():
            title=form.cleaned_data['title']
            description=form.cleaned_data['description']
            category = form.cleaned_data['category']
            price=form.cleaned_data['starting_bid']
            image_init=form.cleaned_data['image']

            if image_init == None:
                image= "https://eagle-sensors.com/wp-content/uploads/unavailable-image.jpg"
            else:
                image=image_init

            listing = AuctionListing(
                user=request.user,
                title=title,
                description=description,
                category = category,
                price=price,
                image=image,
                created = form.created
            )

            listing.save()
            return render(request, "auctions/index.html", {"listings":AuctionListing.objects.all().order_by('created')})

        else:
            return render(request, "auctions/create.html", {"form":form} )

    else:
        return render(request, "auctions/create.html", {"form":NewCreateForm()})

#need to migrate Comments model
@login_required
def listing(request, listing_id):
    listed = AuctionListing.objects.get(pk=listing_id)
    class NewBidForm(forms.Form):
        bid = forms.IntegerField(label='bid',widget=forms.NumberInput(attrs={'placeholder': 'Bid', 'style': 'width: 100px;', 'class': 'form-control'}), min_value=listed.price)

    #initialize forms
    bid_form=NewBidForm()
    comment_form = NewCommentForm()

    #will only be post if a user placed a bid or a comment, or both
    if request.method == "POST":
        if 'bid' in request.POST:
            bid_form=NewBidForm(request.POST)
            if bid_form.is_valid():
                bid=bid_form.cleaned_data['bid']
                listed.price = bid
                listed.save()

        elif 'comment' in request.POST:
            comment_form = NewCommentForm(request.POST)
            if comment_form.is_valid():
                user_comment = comment_form.cleaned_data['comment']

                entry = Comments.objects.create(
                    user=request.user,
                    comment=user_comment,
                    created = datetime.now()
                )
                entry.listing.add(listed)
                entry.save()

        return render(request, "auctions/listing.html", {"listing":listed, "bid_form":NewBidForm(), "comment_form":NewCommentForm(), "comments":Comments.objects.filter(listing=listed.id).order_by('created')})

    else:
        return render(request, "auctions/listing.html", {"listing":listed, "form":NewBidForm(), "comment_form":NewCommentForm(), "comments":Comments.objects.filter(listing=listed.id).order_by('created')})

#list should have access to what we added to our wishlist, need to test and maybe debug
@login_required
def watchlist(request, listing_id=0, action=None):

        #if user just requested to view their watchlist
        if listing_id == 0:
            list = Watchlist.objects.filter(user=request.user).order_by('added')
            return render(request, "auctions/watchlist.html", {"list":list})

        #user wants to add to watchlist (well add remove later)
        elif action=='add':
            #get all attributes associated to a listing using its id
            auction_listing = get_object_or_404(AuctionListing, pk=listing_id)
            auction_listing.in_watchlist = 'yes'
            auction_listing.save()

            #if the user already has an existing watchlist, add auction_listing to it, if they dont, create a watchlist for the user
            watchlist_entry, created = Watchlist.objects.get_or_create(user=request.user)

            watchlist_entry.listing.add(auction_listing)
            watchlist_entry.added = datetime.now()
            watchlist_entry.save()

            list = Watchlist.objects.filter(user=request.user).order_by('added')
            return render(request, "auctions/watchlist.html", {"list":list})

       #remove from watchlist
        else:

            #get all attributes associated to a listing using its id
            auction_listing = get_object_or_404(AuctionListing, pk=listing_id)
            auction_listing.in_watchlist = 'no'
            auction_listing.save()

            watchlist_entry = Watchlist.objects.get(user=request.user)
            watchlist_entry.listing.remove(auction_listing)
            watchlist_entry.save()

            return redirect('listing', listing_id)


    #if this functions called, it means a bid was placed on a listing, update that listings price, keep a count of number of bids, and pass
    #to re render listing page with new bid price
    #make sure bid is greater than current price
