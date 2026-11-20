from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import ProductForm
from .models import Product
from .services import AIServiceError, generate_product_details


def product_list(request):
    products = Product.objects.all()
    return render(request, "products/product_list.html", {"products": products})


def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            try:
                generated_description, product.price = generate_product_details(
                    product.name,
                    product.category,
                )
            except AIServiceError as exc:
                form.add_error(None, str(exc))
            else:
                if not product.description.strip():
                    product.description = generated_description
                product.save()
                messages.success(request, "Product saved with an AI-suggested price in INR.")
                return redirect("product_list")
    else:
        form = ProductForm()

    return render(request, "products/product_form.html", {"form": form})
