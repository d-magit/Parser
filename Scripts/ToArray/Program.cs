using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;

namespace toarray
{
    public class JSON
    {
        public static int movienum = 0;
        public static object[][][] Genres => genres ??= (from genre in (from m2d in JsonConvert.DeserializeObject<Dictionary<string, Dictionary<string, object>[]>>(File.ReadAllText(Environment.CurrentDirectory + "/../../Results/filtered.json")).Values select m2d).ToArray() select (from movie in genre select GetPropertiesForCurrentMovie(movie)).ToArray()).ToArray();
        private static object[][][] genres;
        private static object[] GetPropertiesForCurrentMovie(Dictionary<string, object> movie)
        {
            object[] props = movie.Values.ToArray();
            props[3] = ((JArray)props[3]).ToObject<string[]>();
            return props;
        }

        public static void HashAndCount()
        {
            string ByteArrayToString(byte[] ba)
            {
                StringBuilder hex = new StringBuilder(ba.Length * 2);
                foreach (byte b in ba) hex.AppendFormat("{0:x2}", b);
                return hex.ToString();
            }

            movienum = 0;
            var alreadyin = new HashSet<string>();
            for (var i = 0; i < Genres.Length; i++)
                for (var j = 0; j < Genres[i].Length; j++)
                {
                    if (movienum % 1000 == 0) Console.WriteLine($"Reaching {movienum} movies...");

                    string filename = ByteArrayToString(SHA256.Create().ComputeHash(Encoding.UTF8.GetBytes((string)Genres[i][j][0])));
                    
                    if (!alreadyin.Contains(filename))
                    {
                        movienum++;
                        alreadyin.Add(filename);
                    }
                    if (Genres[i][j].Length != 9)
                    {
                        var temp = Genres[i][j].ToList();
                        temp.Add(filename);
                        Genres[i][j] = temp.ToArray();
                    }
                }
        }
    }

    public class LoadJSON
    {
        static void Main()
        {
            JSON.HashAndCount();
            Console.WriteLine($"Total: {JSON.movienum}.");
            File.WriteAllText(Environment.CurrentDirectory + "/../../Results/toarray.json", JsonConvert.SerializeObject(JSON.Genres));
            Console.ReadLine();
        }
    }
}