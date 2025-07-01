"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button";

interface FilterSidebarProps {
  categories: string[];
  styles: string[];
  onFilterChange: (filters: any) => void;
}

export function FilterSidebar({ categories, styles, onFilterChange }: FilterSidebarProps) {
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [selectedStyles, setSelectedStyles] = useState<string[]>([]);
  const [showPremiumOnly, setShowPremiumOnly] = useState(false);

  const handleCategoryChange = (category: string, checked: boolean) => {
    const updated = checked
      ? [...selectedCategories, category]
      : selectedCategories.filter((c) => c !== category);
    setSelectedCategories(updated);
    updateFilters({ categories: updated });
  };

  const handleStyleChange = (style: string, checked: boolean) => {
    const updated = checked
      ? [...selectedStyles, style]
      : selectedStyles.filter((s) => s !== style);
    setSelectedStyles(updated);
    updateFilters({ styles: updated });
  };

  const updateFilters = (partialFilters: any) => {
    onFilterChange({
      categories: selectedCategories,
      styles: selectedStyles,
      premiumOnly: showPremiumOnly,
      ...partialFilters,
    });
  };

  const clearFilters = () => {
    setSelectedCategories([]);
    setSelectedStyles([]);
    setShowPremiumOnly(false);
    onFilterChange({});
  };

  return (
    <Card className="w-full">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">Filters</CardTitle>
          <Button variant="ghost" size="sm" onClick={clearFilters}>
            Clear all
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Categories */}
        <div>
          <Label className="text-sm font-medium mb-3 block">Categories</Label>
          <div className="space-y-2">
            {categories.map((category) => (
              <div key={category} className="flex items-center space-x-2">
                <Checkbox
                  id={`category-${category}`}
                  checked={selectedCategories.includes(category)}
                  onCheckedChange={(checked) =>
                    handleCategoryChange(category, checked as boolean)
                  }
                />
                <Label htmlFor={`category-${category}`} className="text-sm">
                  {category}
                </Label>
              </div>
            ))}
          </div>
        </div>

        <Separator />

        {/* Styles */}
        <div>
          <Label className="text-sm font-medium mb-3 block">Styles</Label>
          <div className="space-y-2">
            {styles.map((style) => (
              <div key={style} className="flex items-center space-x-2">
                <Checkbox
                  id={`style-${style}`}
                  checked={selectedStyles.includes(style)}
                  onCheckedChange={(checked) =>
                    handleStyleChange(style, checked as boolean)
                  }
                />
                <Label htmlFor={`style-${style}`} className="text-sm">
                  {style}
                </Label>
              </div>
            ))}
          </div>
        </div>

        <Separator />

        {/* Premium Filter */}
        <div className="flex items-center space-x-2">
          <Checkbox
            id="premium-only"
            checked={showPremiumOnly}
            onCheckedChange={(checked) => {
              setShowPremiumOnly(checked as boolean);
              updateFilters({ premiumOnly: checked });
            }}
          />
          <Label htmlFor="premium-only" className="text-sm">
            Premium only
          </Label>
        </div>
      </CardContent>
    </Card>
  );
}