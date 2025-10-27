/**
 * Test Configuration Component
 * 
 * Allows users to configure aptitude test parameters including:
 * - Question count and time limits
 * - Category and difficulty filters
 * - Adaptive algorithm selection
 * - Test customization options
 */

import React, { useState, useEffect } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, Settings, Clock, Target, Brain, Filter } from 'lucide-react';

import { AptitudeService } from '../../services/aptitude';
import type { AptitudeTestConfigRequest, AvailableFilters, AdaptiveAlgorithm } from '../../types/aptitude';

// Validation schema
const configSchema = z.object({
  title: z.string().optional(),
  description: z.string().optional(),
  total_questions: z.number().min(5).max(100).default(20),
  time_limit: z.number().min(300).max(7200).optional(), // 5 minutes to 2 hours
  time_per_question: z.number().min(30).max(600).optional(), // 30 seconds to 10 minutes
  categories: z.array(z.string()).optional(),
  difficulty_levels: z.array(z.number()).optional(),
  company_tags: z.array(z.string()).optional(),
  topic_tags: z.array(z.string()).optional(),
  adaptive_algorithm: z.enum(['random', 'difficulty_based', 'performance_based', 'irt_based', 'balanced']).default('balanced'),
  randomize_questions: z.boolean().default(true),
  randomize_options: z.boolean().default(true),
  allow_review: z.boolean().default(true),
  show_results: z.boolean().default(true),
  passing_score: z.number().min(0).max(100).default(60),
  negative_marking: z.boolean().default(false),
  negative_marking_ratio: z.number().min(0).max(1).default(0.25),
});

type ConfigFormData = z.infer<typeof configSchema>;

interface TestConfigurationProps {
  onConfigSubmit: (config: AptitudeTestConfigRequest) => void;
  isLoading?: boolean;
  initialConfig?: Partial<AptitudeTestConfigRequest>;
}

export const TestConfiguration: React.FC<TestConfigurationProps> = ({
  onConfigSubmit,
  isLoading = false,
  initialConfig = {}
}) => {
  const [availableFilters, setAvailableFilters] = useState<AvailableFilters | null>(null);
  const [filtersLoading, setFiltersLoading] = useState(true);
  const [selectedCategories, setSelectedCategories] = useState<string[]>(initialConfig.categories || []);
  const [selectedCompanies, setSelectedCompanies] = useState<string[]>(initialConfig.company_tags || []);
  const [selectedTopics, setSelectedTopics] = useState<string[]>(initialConfig.topic_tags || []);
  const [selectedDifficulties, setSelectedDifficulties] = useState<number[]>(initialConfig.difficulty_levels || [1, 2, 3, 4, 5]);

  const form = useForm<ConfigFormData>({
    resolver: zodResolver(configSchema),
    defaultValues: {
      title: initialConfig.title || '',
      description: initialConfig.description || '',
      total_questions: initialConfig.total_questions || 20,
      time_limit: initialConfig.time_limit,
      time_per_question: initialConfig.time_per_question,
      adaptive_algorithm: (initialConfig.adaptive_algorithm as any) || 'balanced',
      randomize_questions: initialConfig.randomize_questions ?? true,
      randomize_options: initialConfig.randomize_options ?? true,
      allow_review: initialConfig.allow_review ?? true,
      show_results: initialConfig.show_results ?? true,
      passing_score: initialConfig.passing_score || 60,
      negative_marking: initialConfig.negative_marking || false,
      negative_marking_ratio: initialConfig.negative_marking_ratio || 0.25,
    }
  });

  // Load available filters on component mount
  useEffect(() => {
    const loadFilters = async () => {
      try {
        const filters = await AptitudeService.getAvailableFilters();
        setAvailableFilters(filters);
      } catch (error) {
        console.error('Failed to load available filters:', error);
      } finally {
        setFiltersLoading(false);
      }
    };

    loadFilters();
  }, []);

  const onSubmit = (data: ConfigFormData) => {
    const config: AptitudeTestConfigRequest = {
      ...data,
      categories: selectedCategories.length > 0 ? selectedCategories : undefined,
      company_tags: selectedCompanies.length > 0 ? selectedCompanies : undefined,
      topic_tags: selectedTopics.length > 0 ? selectedTopics : undefined,
      difficulty_levels: selectedDifficulties.length > 0 ? selectedDifficulties : undefined,
    };

    onConfigSubmit(config);
  };

  const handleCategoryToggle = (category: string) => {
    setSelectedCategories(prev =>
      prev.includes(category)
        ? prev.filter(c => c !== category)
        : [...prev, category]
    );
  };

  const handleCompanyToggle = (company: string) => {
    setSelectedCompanies(prev =>
      prev.includes(company)
        ? prev.filter(c => c !== company)
        : [...prev, company]
    );
  };

  const handleTopicToggle = (topic: string) => {
    setSelectedTopics(prev =>
      prev.includes(topic)
        ? prev.filter(t => t !== topic)
        : [...prev, topic]
    );
  };

  const handleDifficultyToggle = (difficulty: number) => {
    setSelectedDifficulties(prev =>
      prev.includes(difficulty)
        ? prev.filter(d => d !== difficulty)
        : [...prev, difficulty]
    );
  };

  const getDifficultyLabel = (level: number): string => {
    const labels = { 1: 'Beginner', 2: 'Easy', 3: 'Medium', 4: 'Hard', 5: 'Expert' };
    return labels[level as keyof typeof labels] || `Level ${level}`;
  };

  const getAlgorithmDescription = (algorithm: string): string => {
    const descriptions = {
      random: 'Questions selected randomly from available pool',
      difficulty_based: 'Questions selected based on difficulty distribution',
      performance_based: 'Questions adapted based on your performance',
      irt_based: 'Advanced Item Response Theory based selection',
      balanced: 'Balanced selection considering multiple factors'
    };
    return descriptions[algorithm as keyof typeof descriptions] || '';
  };

  if (filtersLoading) {
    return (
      <Card className="w-full max-w-4xl mx-auto">
        <CardContent className="flex items-center justify-center py-8">
          <Loader2 className="h-8 w-8 animate-spin" />
          <span className="ml-2">Loading test configuration...</span>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Settings className="h-5 w-5" />
          Configure Aptitude Test
        </CardTitle>
        <CardDescription>
          Customize your test parameters to create a personalized aptitude assessment
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            {/* Basic Configuration */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <Target className="h-4 w-4" />
                Basic Configuration
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <FormField
                  control={form.control}
                  name="title"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Test Title</FormLabel>
                      <FormControl>
                        <Input placeholder="My Aptitude Test" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="total_questions"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Number of Questions</FormLabel>
                      <FormControl>
                        <Input
                          type="number"
                          min={5}
                          max={100}
                          {...field}
                          onChange={e => field.onChange(parseInt(e.target.value))}
                        />
                      </FormControl>
                      <FormDescription>Between 5 and 100 questions</FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <FormField
                control={form.control}
                name="description"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Description (Optional)</FormLabel>
                    <FormControl>
                      <Input placeholder="Test description..." {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <Separator />

            {/* Time Configuration */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <Clock className="h-4 w-4" />
                Time Configuration
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <FormField
                  control={form.control}
                  name="time_limit"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Total Time Limit (minutes)</FormLabel>
                      <FormControl>
                        <Input
                          type="number"
                          min={5}
                          max={120}
                          placeholder="No limit"
                          {...field}
                          onChange={e => field.onChange(e.target.value ? parseInt(e.target.value) * 60 : undefined)}
                          value={field.value ? Math.floor(field.value / 60) : ''}
                        />
                      </FormControl>
                      <FormDescription>Leave empty for no time limit</FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="time_per_question"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Time per Question (seconds)</FormLabel>
                      <FormControl>
                        <Input
                          type="number"
                          min={30}
                          max={600}
                          placeholder="No limit"
                          {...field}
                          onChange={e => field.onChange(e.target.value ? parseInt(e.target.value) : undefined)}
                        />
                      </FormControl>
                      <FormDescription>Leave empty for no per-question limit</FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
            </div>

            <Separator />

            {/* Content Filters */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <Filter className="h-4 w-4" />
                Content Filters
              </h3>

              {/* Categories */}
              {availableFilters?.categories && availableFilters.categories.length > 0 && (
                <div>
                  <FormLabel className="text-sm font-medium">Categories</FormLabel>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {availableFilters.categories.map(category => (
                      <Badge
                        key={category}
                        variant={selectedCategories.includes(category) ? "default" : "outline"}
                        className="cursor-pointer"
                        onClick={() => handleCategoryToggle(category)}
                      >
                        {category}
                      </Badge>
                    ))}
                  </div>
                  <p className="text-sm text-muted-foreground mt-1">
                    {selectedCategories.length === 0 ? 'All categories selected' : `${selectedCategories.length} categories selected`}
                  </p>
                </div>
              )}

              {/* Difficulty Levels */}
              <div>
                <FormLabel className="text-sm font-medium">Difficulty Levels</FormLabel>
                <div className="flex flex-wrap gap-2 mt-2">
                  {[1, 2, 3, 4, 5].map(level => (
                    <Badge
                      key={level}
                      variant={selectedDifficulties.includes(level) ? "default" : "outline"}
                      className="cursor-pointer"
                      onClick={() => handleDifficultyToggle(level)}
                    >
                      {getDifficultyLabel(level)}
                    </Badge>
                  ))}
                </div>
                <p className="text-sm text-muted-foreground mt-1">
                  {selectedDifficulties.length} difficulty levels selected
                </p>
              </div>

              {/* Company Tags */}
              {availableFilters?.company_tags && availableFilters.company_tags.length > 0 && (
                <div>
                  <FormLabel className="text-sm font-medium">Companies</FormLabel>
                  <div className="flex flex-wrap gap-2 mt-2 max-h-32 overflow-y-auto">
                    {availableFilters.company_tags.slice(0, 20).map(company => (
                      <Badge
                        key={company}
                        variant={selectedCompanies.includes(company) ? "default" : "outline"}
                        className="cursor-pointer"
                        onClick={() => handleCompanyToggle(company)}
                      >
                        {company}
                      </Badge>
                    ))}
                  </div>
                  <p className="text-sm text-muted-foreground mt-1">
                    {selectedCompanies.length === 0 ? 'All companies included' : `${selectedCompanies.length} companies selected`}
                  </p>
                </div>
              )}

              {/* Topic Tags */}
              {availableFilters?.topic_tags && availableFilters.topic_tags.length > 0 && (
                <div>
                  <FormLabel className="text-sm font-medium">Topics</FormLabel>
                  <div className="flex flex-wrap gap-2 mt-2 max-h-32 overflow-y-auto">
                    {availableFilters.topic_tags.slice(0, 20).map(topic => (
                      <Badge
                        key={topic}
                        variant={selectedTopics.includes(topic) ? "default" : "outline"}
                        className="cursor-pointer"
                        onClick={() => handleTopicToggle(topic)}
                      >
                        {topic}
                      </Badge>
                    ))}
                  </div>
                  <p className="text-sm text-muted-foreground mt-1">
                    {selectedTopics.length === 0 ? 'All topics included' : `${selectedTopics.length} topics selected`}
                  </p>
                </div>
              )}
            </div>

            <Separator />

            {/* Advanced Configuration */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <Brain className="h-4 w-4" />
                Advanced Configuration
              </h3>

              <FormField
                control={form.control}
                name="adaptive_algorithm"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Question Selection Algorithm</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select algorithm" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {availableFilters?.adaptive_algorithms?.map(algorithm => (
                          <SelectItem key={algorithm} value={algorithm}>
                            {algorithm.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormDescription>
                      {getAlgorithmDescription(field.value)}
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <FormField
                  control={form.control}
                  name="passing_score"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Passing Score (%)</FormLabel>
                      <FormControl>
                        <div className="space-y-2">
                          <Slider
                            min={0}
                            max={100}
                            step={5}
                            value={[field.value]}
                            onValueChange={([value]) => field.onChange(value)}
                          />
                          <div className="text-center text-sm text-muted-foreground">
                            {field.value}%
                          </div>
                        </div>
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="negative_marking_ratio"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Negative Marking Ratio</FormLabel>
                      <FormControl>
                        <div className="space-y-2">
                          <Slider
                            min={0}
                            max={1}
                            step={0.05}
                            value={[field.value]}
                            onValueChange={([value]) => field.onChange(value)}
                            disabled={!form.watch('negative_marking')}
                          />
                          <div className="text-center text-sm text-muted-foreground">
                            {(field.value * 100).toFixed(0)}%
                          </div>
                        </div>
                      </FormControl>
                      <FormDescription>
                        Penalty for incorrect answers (as ratio of positive marks)
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              {/* Test Options */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-4">
                  <FormField
                    control={form.control}
                    name="negative_marking"
                    render={({ field }) => (
                      <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3">
                        <div className="space-y-0.5">
                          <FormLabel>Negative Marking</FormLabel>
                          <FormDescription>
                            Deduct marks for incorrect answers
                          </FormDescription>
                        </div>
                        <FormControl>
                          <Switch
                            checked={field.value}
                            onCheckedChange={field.onChange}
                          />
                        </FormControl>
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="randomize_questions"
                    render={({ field }) => (
                      <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3">
                        <div className="space-y-0.5">
                          <FormLabel>Randomize Questions</FormLabel>
                          <FormDescription>
                            Shuffle question order
                          </FormDescription>
                        </div>
                        <FormControl>
                          <Switch
                            checked={field.value}
                            onCheckedChange={field.onChange}
                          />
                        </FormControl>
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="randomize_options"
                    render={({ field }) => (
                      <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3">
                        <div className="space-y-0.5">
                          <FormLabel>Randomize Options</FormLabel>
                          <FormDescription>
                            Shuffle answer choices
                          </FormDescription>
                        </div>
                        <FormControl>
                          <Switch
                            checked={field.value}
                            onCheckedChange={field.onChange}
                          />
                        </FormControl>
                      </FormItem>
                    )}
                  />
                </div>

                <div className="space-y-4">
                  <FormField
                    control={form.control}
                    name="allow_review"
                    render={({ field }) => (
                      <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3">
                        <div className="space-y-0.5">
                          <FormLabel>Allow Review</FormLabel>
                          <FormDescription>
                            Let users review answers before submitting
                          </FormDescription>
                        </div>
                        <FormControl>
                          <Switch
                            checked={field.value}
                            onCheckedChange={field.onChange}
                          />
                        </FormControl>
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="show_results"
                    render={({ field }) => (
                      <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3">
                        <div className="space-y-0.5">
                          <FormLabel>Show Results</FormLabel>
                          <FormDescription>
                            Display detailed results after completion
                          </FormDescription>
                        </div>
                        <FormControl>
                          <Switch
                            checked={field.value}
                            onCheckedChange={field.onChange}
                          />
                        </FormControl>
                      </FormItem>
                    )}
                  />
                </div>
              </div>
            </div>

            {/* Submit Button */}
            <div className="flex justify-end pt-4">
              <Button type="submit" disabled={isLoading} className="min-w-32">
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Creating...
                  </>
                ) : (
                  'Create Test'
                )}
              </Button>
            </div>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
};