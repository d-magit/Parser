using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace removegenres
{
    public class JSON
    {
        public static int movienum = 0;
        public static HashSet<object[]> Movies = new HashSet<object[]>();
        public static object[][][] Genres => genres ??= JsonConvert.DeserializeObject<object[][][]>(File.ReadAllText(Environment.CurrentDirectory + "/../../Results/toarray.json"));
        private static object[][][] genres;
        public static void GenresRemoval()
        {
            movienum = 0;
            var alreadyin = new HashSet<string>();
            for (var i = 0; i < Genres.Length; i++)
                for (var j = 0; j < Genres[i].Length; j++)
                {
                    if (movienum % 1000 == 0) Console.WriteLine($"Reaching {movienum} movies...");
                    string hash = (string)Genres[i][j][8];
                    if (!alreadyin.Contains(hash))
                    {
                        Movies.Add(Genres[i][j]);
                        movienum++;
                        alreadyin.Add(hash);
                    }
                }
        }
    }

    public class LoadJSON
    {
        static void Main()
        {
            JSON.GenresRemoval();
            Console.WriteLine($"Total after removal: {JSON.movienum}.");
            File.WriteAllText(Environment.CurrentDirectory + "/../../Results/removegenres.json", JsonConvert.SerializeObject(JSON.Movies));
            Console.ReadLine();
        }
    }
}