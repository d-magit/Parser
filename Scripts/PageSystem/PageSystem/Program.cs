
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace PageSystem
{
    class Program
    {
        public static string[] Genres = new string[18] { "action", "adventure", "animation", "comedy", "crime", "documentary", "drama", "family", "fantasy", "history", "horror", "music", "mystery", "romance", "sci-fi", "thriller", "war", "western" };
        public static int[] Years = new int[21] { 2021, 2020, 2019, 2018, 2017, 2016, 2015, 2014, 2013, 2012, 2011, 2010, 2000, 1990, 1980, 1970, 1960, 1950, 1940, 1930, 1920 };
        public static int[] Rating = new int[11] { 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0 };
        public static object[][] Movies = (from movie in JsonConvert.DeserializeObject<object[][]>(File.ReadAllText("../../../../../../Results/linkspoofed.json"))
                                           select new Func<object[], object[]>(Movie =>
                                           {
                                               List<object> movie0 = Movie.ToList();
                                               movie0[2] = ((JArray)movie0[2]).ToObject<string[]>();
                                               return movie0.ToArray();
                                           }).Invoke(movie)).ToArray().ToArray();
        public static int RatingSorting(object[] mov0, object[] mov1) => SafeParseFloat((string)mov0[3]).CompareTo(SafeParseFloat((string)mov1[3]));
        public static int YearSorting(object[] mov0, object[] mov1) => SafeParseInt((string)mov0[4]).CompareTo(SafeParseInt((string)mov1[4]));
        public static int AlphabeticalSorting(object[] mov0, object[] mov1) => ((string)mov0[0]).CompareTo((string)mov1[0]);
        public static int SafeParseInt(string s)
        {
            int result;
            int.TryParse(s, out result);
            return result;
        }
        public static float SafeParseFloat(string s)
        {
            float result;
            float.TryParse(s, out result);
            return result;
        }


        static void Main(string[] args)
        {
            var Final = new int[3][][][][]; // FilterBy (Genres, Rating, Year), SortBy (Rating, Year, Alphabetical), Genre/Rate/Year Index, Page, Movie 
            object[][] RatingSort = Movies.OrderByDescending(o => SafeParseFloat((string)o[3])).ToArray();
            object[][] YearSort = Movies.OrderByDescending(o => SafeParseInt((string)o[4])).ToArray();
            object[][] AlphabeticalSort = Movies.OrderBy(o => (string)o[0]).ToArray();
            for (var a = 0; a < 3; a++) // a = Filter By [Genres, Rating, Year]
            {
                Final[a] = new int[3][][][];
                for (var b = 0; b < 3; b++) // b = Sort By: [Rating, Year, Alphabetical]
                {
                    object[][] Movies = b switch
                    {
                        // Year
                        1 => YearSort,
                        // Alphabetical
                        2 => AlphabeticalSort,
                        // Rating
                        _ => RatingSort,
                    };
                    int LoopLen = a switch
                    {
                        // Rating
                        1 => 11,
                        // Year
                        2 => 21,
                        // Genres
                        _ => 18,
                    };
                    Final[a][b] = new int[LoopLen][][];
                    for (var c = 0; c < LoopLen; c++)
                        Final[a][b][c] = SetMediaForFilter(Movies, a, c);
                }
            }
            File.WriteAllText("../../../../../../Results/Pages.json", JsonConvert.SerializeObject(Final));
        }

        public static int[][] SetMediaForFilter(object[][] Movies, int Filter, int Index)
        {
            var SelectedMovies = new List<object[]>();
            switch (Filter)
            {
                case 2:
                    int CurrentYear = Years[Index];
                    if (CurrentYear > 2010)
                        foreach (object[] Movie in Movies)
                        { if (SafeParseInt((string)Movie[4]) == CurrentYear) SelectedMovies.Add(Movie); }
                    else if (CurrentYear <= 2010 && CurrentYear > 1920)
                        foreach (object[] Movie in Movies)
                        {
                            int MovieYear = SafeParseInt((string)Movie[4]);
                            if (MovieYear <= CurrentYear && MovieYear > CurrentYear - 10) SelectedMovies.Add(Movie);
                        }
                    else
                        foreach (object[] Movie in Movies)
                            if (SafeParseInt((string)Movie[4]) <= CurrentYear) SelectedMovies.Add(Movie);
                    break;
                case 1:
                    int CurrentRating = Rating[Index];
                    foreach (object[] Movie in Movies)
                    {
                        float MovieRating = SafeParseFloat((string)Movie[3]);
                        if (MovieRating <= CurrentRating && MovieRating > CurrentRating - 1) SelectedMovies.Add(Movie);
                    }
                    break;
                default:
                    string CurrentGenre = Genres[Index];
                    foreach (object[] Movie in Movies)
                        foreach (string Genre in (object[])Movie[2])
                            if (CurrentGenre == Genre) SelectedMovies.Add(Movie);
                    break;
            }
            return CreatePages(SelectedMovies);
        }

        public static int[][] CreatePages(List<object[]> SelectedMovies)
        {
            HashSet<int[]> PageArr = new();
            HashSet<int> CurrentPage = new();
            int CurrentMovieNum = 0;
            for (var k = 0; k < SelectedMovies.Count; k++)
            {
                if (CurrentMovieNum % 100 == 0 && CurrentMovieNum != 0)
                {
                    PageArr.Add(CurrentPage.ToArray());
                    CurrentPage = new HashSet<int>();
                }
                CurrentPage.Add(Array.FindIndex(Movies, movie => (string)movie[7] == (string)SelectedMovies[k][7]));
                CurrentMovieNum++;
            }
            PageArr.Add(CurrentPage.ToArray());
            return PageArr.ToArray();
        }
    }
}
